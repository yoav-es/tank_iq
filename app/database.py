import sqlite3
import logging # <-- NEW: Import logging
from typing import Optional, Generator, List, Dict, Any
from contextlib import contextmanager

# Import the necessary local modules and FuelEntryUpdate
from .models import FuelEntryCreate, FuelEntryDB, FuelEntryUpdate, OverallStats 
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
            # INFO Log: Confirm table creation/existence
            logger.info("Database initialized successfully and 'fuel_entries' table is ready.")
    except sqlite3.Error as e:
        # CRITICAL Log: Failure during DB setup
        logger.critical(f"CRITICAL ERROR during database initialization: {e}")
        # Pass silently during testing/init phase (as per original logic)
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

# --- 4. CRUD Operations ---

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
            
            # INFO Log: Successful insertion
            logger.info(f"Entry inserted successfully. New ID: {new_id}, Liters: {entry.liters}.")
            
            # Read the newly inserted row to get all fields and return the model
            row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (new_id,)).fetchone()
            
            if row:
                return _row_to_fuel_entry_db(row)
            return None
            
    except sqlite3.Error as e:
        # ERROR Log: Failed insertion
        logger.error(f"Database ERROR: Failed to insert new entry. Details: {e}")
        return None

def read_entry(entry_id: int) -> Optional[FuelEntryDB]:
    """Retrieves a single entry by ID and converts it to FuelEntryDB."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (entry_id,)).fetchone()
        
        if row:
            # INFO Log: Successful retrieval
            logger.info(f"Entry retrieved successfully. ID: {entry_id}.")
            # Use the helper function to return the full Pydantic model
            return _row_to_fuel_entry_db(row)
            
        # WARNING Log: Entry not found
        logger.warning(f"Attempted to retrieve non-existent entry ID: {entry_id}.")
        return None

# Retrieves raw entries for overall statistics calculation
def get_all_entries_raw() -> List[Dict[str, Any]]:
    """Retrieves all entries from the database, returning raw dictionaries."""
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM fuel_entries ORDER BY date DESC").fetchall()
            # INFO Log: Successful raw retrieval
            logger.info(f"Retrieved {len(rows)} raw entries for statistics calculation.")
            return [dict(row) for row in rows] 
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to retrieve raw entries. Details: {e}")
        return []

# Retrieves processed entries for the response body
def get_all_entries_processed() -> List[FuelEntryDB]:
    """Retrieves all entries, calculates derived fields, and returns FuelEntryDB models."""
    try:
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM fuel_entries ORDER BY date DESC").fetchall()
            # INFO Log: Successful processed retrieval
            logger.info(f"Retrieved and processed {len(rows)} entries for API response.")
            # CRITICAL FIX: Process every row using the helper function
            return [_row_to_fuel_entry_db(row) for row in rows]
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to retrieve processed entries. Details: {e}")
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

    # Read and return the updated entry only if the update was successful
    if row_count > 0:
        # INFO Log: Successful update
        logger.info(f"Entry ID {entry_id} updated successfully.")
        return read_entry(entry_id) # Uses a new connection via read_entry
    
    # WARNING Log: Entry not found for update
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
                # INFO Log: Successful deletion
                logger.info(f"Entry ID {entry_id} deleted successfully.")
                return True
            else:
                # WARNING Log: Entry not found for deletion
                logger.warning(f"Attempted to delete non-existent entry ID: {entry_id}.")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Database ERROR: Failed to delete entry ID {entry_id}. Details: {e}")
        return False