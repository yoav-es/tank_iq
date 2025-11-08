# app/database.py

import sqlite3
from typing import Optional, Generator, List, Dict, Any
from contextlib import contextmanager

# Import the necessary local modules
from .models import FuelEntryCreate, FuelEntryDB 
from .utils import calculate_entry_stats # Used to populate derived fields

DATABASE_NAME = "fuel_log.db"

# --- 1. Connection Functions ---

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
    except sqlite3.Error as e:
        # Pass silently during testing/init phase
        pass

# --- 2. CRUD Operations ---

def insert_entry(entry: FuelEntryCreate) -> Optional[int]:
    """Inserts a new FuelEntry object into the database."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO fuel_entries (date, liters, price_per_liter, distance, notes)
                VALUES (?, ?, ?, ?, ?)
                """,
                # Access Pydantic data using dot notation
                (entry.date, entry.liters, entry.price_per_liter, entry.distance, entry.notes)
            )
            conn.commit()
            return cursor.lastrowid
    except sqlite3.Error:
        return None

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

def read_entry(entry_id: int) -> Optional[FuelEntryDB]:
    """Retrieves a single entry by ID and converts it to FuelEntryDB."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (entry_id,)).fetchone()
        
        if row:
            # Use the helper function to return the full Pydantic model
            return _row_to_fuel_entry_db(row)
            
        return None

def list_entries() -> List[Dict[str, Any]]:
    """Retrieves all entries from the database, returning raw dicts/Rows."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM fuel_entries ORDER BY date DESC").fetchall()
        return [dict(row) for row in rows] 

def update_entry(entry_id: int, entry: FuelEntryCreate) -> bool:
    """Updates an existing entry based on its ID."""
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
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False

def delete_entry(entry_id: int) -> bool:
    """Deletes an entry by ID."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM fuel_entries WHERE id = ?", (entry_id,))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error:
        return False