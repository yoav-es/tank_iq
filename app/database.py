import sqlite3
import logging
from typing import Optional, Generator, List, Dict, Any
from contextlib import contextmanager
from datetime import date 

# Import the necessary local modules and FuelEntryUpdate
from .models import FuelEntryCreate, FuelEntryDB, FuelEntryUpdate, TimePeriodStats 
from .utils import calculate_entry_stats, get_overall_stats

# --- 1. LOGGING SETUP ---
logger = logging.getLogger(__name__)
# ------------------------

DATABASE_NAME = "fuel_log.db"

# --- 2. Connection Functions ---

def create_db_connection(db_path: str = DATABASE_NAME) -> sqlite3.Connection:
    """Creates and returns a new database connection."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    return conn

@contextmanager
def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager to handle database connection lifecycle (open and close).
    """
    conn = create_db_connection()
    try:
        yield conn
    finally:
        # Ensures the connection is closed even if errors occur
        conn.close()

def init_db() -> None:
    """Initializes the database by creating the fuel_entries table."""
    try:
        with get_db() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fuel_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    liters REAL NOT NULL,
                    price_per_liter REAL NOT NULL,
                    distance REAL NOT NULL,
                    notes TEXT
                )
            """)
            conn.commit()
            logger.info("Database initialized successfully and 'fuel_entries' table is ready.")
    except sqlite3.Error as e:
        logger.critical(f"CRITICAL ERROR during database initialization: {e}")
        pass

# --- 3. Helper ---

def _row_to_fuel_entry_db(row: sqlite3.Row) -> FuelEntryDB:
    """Helper to convert a sqlite3.Row into the Pydantic FuelEntryDB model."""
    entry_dict = dict(row)
    
    # Calculate derived fields using the utility function
    stats = calculate_entry_stats(
        entry_dict['liters'], entry_dict['price_per_liter'], entry_dict['distance']
    )
    
    # Merge stats into the entry data and validate with Pydantic
    full_data = {**entry_dict, **stats}
    return FuelEntryDB.model_validate(full_data)

# --- 4. CRUD and Retrieval Operations ---

def insert_entry(entry: FuelEntryCreate) -> Optional[FuelEntryDB]:
    """Inserts a new FuelEntry object into the database and returns the created entry."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO fuel_entries (date, liters, price_per_liter, distance, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                (entry.date, entry.liters, entry.price_per_liter, entry.distance, entry.notes)
            )
            conn.commit()
            new_id = cursor.lastrowid
            
            logger.info(f"Entry inserted successfully. New ID: {new_id}, Liters: {entry.liters}.")
            
            row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (new_id,)).fetchone()
            
            if row:
                return _row_to_fuel_entry_db(row)
            return None
            
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to insert new entry. Details: {e}")
        return None

def read_entry(entry_id: int) -> Optional[FuelEntryDB]:
    """Retrieves a single entry by ID and converts it to FuelEntryDB."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (entry_id,)).fetchone()
        
        if row:
            logger.info(f"Entry retrieved successfully. ID: {entry_id}.")
            return _row_to_fuel_entry_db(row)
            
        logger.warning(f"Attempted to retrieve non-existent entry ID: {entry_id}.")
        return None

def get_entries_raw(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieves entries, optionally filtered by date range, returning raw dictionaries.
    Used for CSV export and overall stats.
    """
    try:
        with get_db() as conn:
            query = "SELECT * FROM fuel_entries"
            params = []
            
            if start_date and end_date:
                query += " WHERE date BETWEEN ? AND ?"
                params = [start_date, end_date]
            elif start_date:
                query += " WHERE date >= ?"
                params = [start_date]
            elif end_date:
                query += " WHERE date <= ?"
                params = [end_date]

            query += " ORDER BY date DESC"
            
            rows = conn.execute(query, params).fetchall()
            
            logger.info(f"Retrieved {len(rows)} raw entries with date filter.")
            return [dict(row) for row in rows] 
            
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to retrieve raw entries. Details: {e}")
        return []

def get_all_entries_raw() -> List[Dict[str, Any]]:
    """Helper function to retrieve ALL entries raw."""
    return get_entries_raw()


def get_all_entries_processed() -> List[FuelEntryDB]:
    """Retrieves all entries, calculates derived fields, and returns FuelEntryDB models."""
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM fuel_entries ORDER BY date DESC").fetchall()
            logger.info(f"Retrieved and processed {len(rows)} entries for API response.")
            return [_row_to_fuel_entry_db(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to retrieve processed entries. Details: {e}")
        return []

# --- NEW: Statistical Insight Functions ---

def get_monthly_stats() -> List[TimePeriodStats]:
    """Calculates and returns statistics aggregated by month (YYYY-MM)."""
    try:
        with get_db() as conn:
            # Group by year and month (YYYY-MM)
            query = """
                SELECT 
                    strftime('%Y-%m', date) as period,
                    SUM(liters) as total_liters,
                    SUM(distance) as total_distance,
                    SUM(liters * price_per_liter) as total_cost,
                    COUNT(id) as count
                FROM fuel_entries
                GROUP BY period
                ORDER BY period DESC
            """
            rows = conn.execute(query).fetchall()
            
            results = []
            for row in rows:
                row_dict = dict(row)
                
                # Calculate derived metrics
                total_liters = row_dict['total_liters']
                total_distance = row_dict['total_distance']
                total_cost = row_dict['total_cost']
                
                # Handle division by zero for averages
                avg_km_per_liter = total_distance / total_liters if total_liters else 0.0
                avg_cost_per_liter = total_cost / total_liters if total_liters else 0.0

                results.append(TimePeriodStats(
                    period_label=row_dict['period'],
                    total_liters=round(total_liters, 2),
                    total_cost=round(total_cost, 2),
                    total_distance=round(total_distance, 2),
                    count=row_dict['count'],
                    average_km_per_liter=round(avg_km_per_liter, 2),
                    average_cost_per_liter=round(avg_cost_per_liter, 2)
                ))
            
            logger.info(f"Calculated {len(results)} monthly statistical periods.")
            return results
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to retrieve monthly stats. Details: {e}")
        return []

def get_yearly_stats() -> List[TimePeriodStats]:
    """Calculates and returns statistics aggregated by year (YYYY)."""
    try:
        with get_db() as conn:
            # Group by year (YYYY)
            query = """
                SELECT 
                    strftime('%Y', date) as period,
                    SUM(liters) as total_liters,
                    SUM(distance) as total_distance,
                    SUM(liters * price_per_liter) as total_cost,
                    COUNT(id) as count
                FROM fuel_entries
                GROUP BY period
                ORDER BY period DESC
            """
            rows = conn.execute(query).fetchall()
            
            results = []
            for row in rows:
                row_dict = dict(row)
                
                # Calculate derived metrics
                total_liters = row_dict['total_liters']
                total_distance = row_dict['total_distance']
                total_cost = row_dict['total_cost']
                
                # Handle division by zero for averages
                avg_km_per_liter = total_distance / total_liters if total_liters else 0.0
                avg_cost_per_liter = total_cost / total_liters if total_liters else 0.0

                results.append(TimePeriodStats(
                    period_label=row_dict['period'],
                    total_liters=round(total_liters, 2),
                    total_cost=round(total_cost, 2),
                    total_distance=round(total_distance, 2),
                    count=row_dict['count'],
                    average_km_per_liter=round(avg_km_per_liter, 2),
                    average_cost_per_liter=round(avg_cost_per_liter, 2)
                ))

            logger.info(f"Calculated {len(results)} yearly statistical periods.")
            return results
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to retrieve yearly stats. Details: {e}")
        return []


def update_entry(entry_id: int, entry: FuelEntryUpdate) -> Optional[FuelEntryDB]:
    """Updates an existing entry based on its ID and returns the updated entry."""
    row_count = 0
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE fuel_entries 
                SET date=?, liters=?, price_per_liter=?, distance=?, notes=?
                WHERE id=?
                """,
                (entry.date, entry.liters, entry.price_per_liter, entry.distance, entry.notes, entry_id)
            )
            conn.commit()
            row_count = cursor.rowcount
            
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to update entry ID {entry_id}. Details: {e}")
        return None

    if row_count > 0:
        logger.info(f"Entry ID {entry_id} updated successfully.")
        return read_entry(entry_id) 
    
    logger.warning(f"Attempted to update non-existent entry ID: {entry_id}.")
    return None

def delete_entry(entry_id: int) -> bool:
    """Deletes an entry by ID."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fuel_entries WHERE id = ?", (entry_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Entry ID {entry_id} deleted successfully.")
                return True
            else:
                logger.warning(f"Attempted to delete non-existent entry ID: {entry_id}.")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to delete entry ID {entry_id}. Details: {e}")
        return False