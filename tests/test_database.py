# tests/test_database.py

import pytest
import sqlite3
from faker import Faker
from app import database
from app.models import FuelEntry 

# Initialize Faker
fake = Faker()

# Helper function to generate unique test data
def create_fake_entry():
    """Generates a realistic, random FuelEntry instance."""
    return FuelEntry(
        date=fake.date_between(start_date='-1y', end_date='today').isoformat(),
        liters=fake.pyfloat(left_digits=2, right_digits=2, positive=True, min_value=10, max_value=80),
        price_per_liter=fake.pyfloat(left_digits=1, right_digits=3, positive=True, min_value=1.0, max_value=2.5),
        distance=fake.pyfloat(left_digits=3, right_digits=1, positive=True, min_value=100, max_value=800),
        notes=fake.sentence(nb_words=5) if fake.boolean(chance_of_getting_true=50) else ""
    )

# Pytest Fixture for Isolated DB
@pytest.fixture
def clean_db(mocker):
    """
    Creates an isolated, in-memory SQLite database and mocks the app.database
    connection function to use it.
    """
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    
    # Use mocker to ensure all calls to get a DB connection use this in-memory one
    mocker.patch('app.database.create_db_connection', return_value=conn)
    
    database.init_db()
    yield conn
    conn.close()

# --- CRUD Tests ---

def test_insert_and_list_multiple(clean_db):
    """Tests inserting multiple unique entries (using Faker) and verifying count."""
    num_entries = 5
    for _ in range(num_entries):
        # Faker ensures each entry is unique and realistic
        database.insert_entry(create_fake_entry())
    
    entries = database.list_entries()
    assert len(entries) == num_entries

def test_read_entry_exists_and_not_exists(clean_db):
    original_entry = create_fake_entry()
    original_entry.liters = 42.42
    new_id = database.insert_entry(original_entry)

    # ADD THIS CHECK:
    assert new_id is not None, "Insertion failed, cannot proceed with read test." 
    
    # Now, Pylance is satisfied that new_id is definitely an int here:
    retrieved = database.read_entry(new_id)
    assert retrieved is not None
    assert retrieved['liters'] == 42.42

def test_update_entry(clean_db):
    """Tests updating an entry with new, unique data (using Faker)."""
    entry_id = database.insert_entry(create_fake_entry())
    
    # --- ADDED CHECK ---
    assert entry_id is not None, "Failed to insert entry for update test."
    
    # Create new, unique data for the update
    updated_entry = create_fake_entry()
    updated_entry.liters = 99.0 
    updated_entry.notes = "Updated Note"
    
    success = database.update_entry(entry_id, updated_entry)
    assert success is True
    
    retrieved = database.read_entry(entry_id)
    # Verify the unique fields were updated correctly
    assert retrieved is not None, "Failed to retrieve updated entry." # Also added check for read_entry
    assert retrieved['liters'] == 99.0
    assert retrieved['notes'] == "Updated Note"
    
def test_delete_entry(clean_db):
    """Tests successful deletion and handles attempts to delete non-existent IDs."""
    entry_id = database.insert_entry(create_fake_entry())
    
    # --- ADDED CHECK ---
    assert entry_id is not None, "Failed to insert entry for delete test."
    
    assert database.delete_entry(entry_id) is True
    assert database.read_entry(entry_id) is None
    
    # Non-existent ID test now uses an ID we know won't exist
    assert database.delete_entry(entry_id + 100) is False