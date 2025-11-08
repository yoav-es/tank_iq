# tests/test_database.py

import pytest
import sqlite3
import unittest.mock
from faker import Faker
# Import the actual application modules
from app import database
# Import Pydantic models for testing the interface
from app.models import FuelEntryCreate, FuelEntryDB 

# Initialize Faker for generating realistic test data
fake = Faker()

# Helper function to generate unique test data (RETURNS PYDANTIC MODEL)
def _create_fake_entry() -> FuelEntryCreate: # <-- RENAMED
    """Generates a realistic, random FuelEntryCreate instance."""
    return FuelEntryCreate(
        date=fake.date_between(start_date='-1y', end_date='today').isoformat(),
        liters=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=10, max_value=80),
        price_per_liter=fake.pyfloat(left_digits=1, right_digits=3, positive=True, min_value=1.0, max_value=2.5),
        distance=fake.pyfloat(left_digits=3, right_digits=1, positive=True, min_value=100, max_value=800),
        notes=fake.sentence(nb_words=5) if fake.boolean(chance_of_getting_true=50) else None
    )

# --- Fixture to handle in-memory database setup ---

@pytest.fixture
def clean_db(mocker):
    """
    Mocks the get_db context manager to use an in-memory database (:memory:).
    This setup prevents external files/locks and minimizes the connection closure issue
    by controlling the lifecycle.
    """
    # 1. Create the in-memory connection
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # 2. Mock the logger dependency (if present, harmless if not)
    try:
        mocker.patch('app.logger')
    except AttributeError:
        pass

    # 3. Initialize the database schema on the temporary connection
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

    # 4. Mock the app.database.get_db() function
    mocker.patch('app.database.get_db', 
                 return_value=unittest.mock.MagicMock(
                     # When 'with get_db()' is entered, return the open connection
                     __enter__=lambda self: conn, 
                     # When 'with get_db()' is exited, do nothing (preventing conn.close() from running)
                     __exit__=lambda self, *args: None
                 ))
    
    yield conn
    
    # 5. Ensure the connection is closed after the entire test suite finishes
    conn.close()

# --- CRUD Tests ---

def test_insert_and_list_multiple(clean_db):
    """Tests inserting multiple entries and verifying the count and data types."""
    num_entries = 4
    
    for _ in range(num_entries):
        database.insert_entry(_create_fake_entry()) # <-- CALL UPDATED
    
    entries = database.list_entries()
    
    assert len(entries) == num_entries
    assert isinstance(entries, list)
    assert all(isinstance(e, dict) for e in entries)

def test_read_entry_exists(clean_db):
    """Tests retrieving a single entry by ID."""
    original_entry = _create_fake_entry() # <-- CALL UPDATED
    original_entry.liters = 55.5
    
    new_id = database.insert_entry(original_entry)

    assert new_id is not None
    
    retrieved = database.read_entry(new_id)
    
    assert retrieved is not None
    assert isinstance(retrieved, FuelEntryDB)
    assert retrieved.liters == 55.5
    assert retrieved.total_cost == round(original_entry.liters * original_entry.price_per_liter, 2)
    

def test_read_entry_not_exists(clean_db):
    """Tests that attempting to read a non-existent ID returns None."""
    retrieved = database.read_entry(99999)
    assert retrieved is None

def test_update_entry(clean_db):
    """Tests updating an existing entry."""
    entry_id = database.insert_entry(_create_fake_entry()) # <-- CALL UPDATED
    assert entry_id is not None
    
    # Create new Pydantic model for the update
    updated_entry = _create_fake_entry() # <-- CALL UPDATED
    updated_entry.liters = 100.0 
    updated_entry.notes = "Updated Test Note"
    
    success = database.update_entry(entry_id, updated_entry)
    assert success is True
    
    # Verify the update by reading the entry back
    retrieved = database.read_entry(entry_id)
    
    assert retrieved is not None
    assert retrieved.liters == 100.0
    assert retrieved.notes == "Updated Test Note"
    
def test_delete_entry(clean_db):
    """Tests successful deletion and handles attempts to delete non-existent IDs."""
    entry_id = database.insert_entry(_create_fake_entry()) # <-- CALL UPDATED
    assert entry_id is not None
    
    # Test successful deletion
    assert database.delete_entry(entry_id) is True
    assert database.read_entry(entry_id) is None
    
    # Test deleting a non-existent ID
    assert database.delete_entry(entry_id + 100) is False