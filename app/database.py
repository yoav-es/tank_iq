# app/database.py

import sqlite3
from typing import Optional
from contextlib import contextmanager
from app.models import FuelEntry 

DB_NAME = "tankiq.db"

# --- Connection Management ---

def create_db_connection() -> sqlite3.Connection:
    """
    Creates and configures a new SQLite connection.
    Configures the connection to allow accessing columns by name 
    (sqlite3.Row factory).

    Returns:
        sqlite3.Connection: The active database connection.
    """
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """
    Provides a context manager for safe database connection handling.

    This ensures the connection is automatically closed upon exiting the 
    'with' block, even if exceptions occur.

    Yields:
        sqlite3.Connection: The active database connection object.
    """
    conn = create_db_connection()
    try:
        yield conn
    finally:
        conn.close()

# --- Schema Initialization ---

def init_db():
    """
    Initializes the SQLite database and creates the 'fuel_entries' table 
    if it does not already exist.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
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

# Call once to ensure the database is ready on module import
init_db()


# --- CRUD Operations ---

def insert_entry(entry: FuelEntry) -> Optional[int]: 
    """
    Inserts a new FuelEntry object into the database.

    Args:
        entry (FuelEntry): The fuel entry object to insert.

    Returns:
        int: The ID of the newly created entry.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fuel_entries (date, liters, price_per_liter, distance, notes)
            VALUES (?, ?, ?, ?, ?)
        """, (
            entry.date,
            entry.liters,
            entry.price_per_liter,
            entry.distance,
            entry.notes
        ))
        conn.commit()
        # Returns the ID of the last row inserted
        return cursor.lastrowid


def list_entries() -> list[sqlite3.Row]:
    """
    Retrieves all fuel entries from the database.

    Entries are ordered chronologically by date and ID.

    Returns:
        list[sqlite3.Row]: A list of dict-like row objects representing all entries.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fuel_entries ORDER BY date ASC, id ASC")
        return cursor.fetchall()


def read_entry(entry_id: int) -> Optional[sqlite3.Row]:
    """
    Retrieves a single fuel entry by its unique ID.

    Args:
        entry_id (int): The ID of the entry to retrieve.

    Returns:
        sqlite3.Row | None: The dict-like row object if found, otherwise None.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fuel_entries WHERE id = ?", (entry_id,))
        return cursor.fetchone()


def update_entry(entry_id: int, updated_entry: FuelEntry) -> bool:
    """
    Updates an existing fuel entry in the database.

    Args:
        entry_id (int): The ID of the entry to update.
        updated_entry (FuelEntry): The object containing the new data.

    Returns:
        bool: True if the entry was successfully updated, False if the ID was not found.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE fuel_entries
            SET date = ?, liters = ?, price_per_liter = ?, distance = ?, notes = ?
            WHERE id = ?
        """, (
            updated_entry.date,
            updated_entry.liters,
            updated_entry.price_per_liter,
            updated_entry.distance,
            updated_entry.notes,
            entry_id
        ))
        conn.commit()
        return cursor.rowcount > 0


def delete_entry(entry_id: int) -> bool:
    """
    Deletes a fuel entry from the database by ID.

    Args:
        entry_id (int): The ID of the entry to delete.

    Returns:
        bool: True if the entry was successfully deleted, False if the ID was not found.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fuel_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0