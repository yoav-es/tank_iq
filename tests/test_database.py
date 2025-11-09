# tests/test_database.py

import pytest
import os
import sqlite3
# Added FuelEntryUpdate to fix the Pylance error
from app.models import FuelEntryCreate, FuelEntryDB, FuelEntryUpdate 
from app.database import (
    init_db,
    insert_entry,
    read_entry,
    update_entry,
    delete_entry,
    get_all_entries_raw,
    get_all_entries_processed,
    DATABASE_NAME
)

# --- Shared Test Data ---

VALID_CREATE_DATA = FuelEntryCreate(
    date="2024-10-25",
    liters=50.5,
    price_per_liter=1.55,
    distance=450.0,
    notes="Highway driving"
)

ANOTHER_CREATE_DATA = FuelEntryCreate(
    date="2024-10-26",
    liters=45.6,
    price_per_liter=1.50,
    distance=785.0,
    notes="Commuting"
)

# --- Fixtures and Setup ---

@pytest.fixture(scope="session", autouse=True)
def setup_teardown_db():
    """Fixture to ensure a fresh, empty database for testing."""
    init_db()
    yield
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

@pytest.fixture(autouse=True)
def clean_db():
    """Fixture to clear the table before each individual test."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM fuel_entries")
    conn.commit()
    conn.close()

# --- Tests ---

def test_insert_and_read_entry():
    """Tests inserting an entry and retrieving it with calculated fields."""
    
    inserted_entry = insert_entry(VALID_CREATE_DATA)
    assert inserted_entry is not None
    assert inserted_entry.id is not None
    
    retrieved_entry = read_entry(inserted_entry.id)
    assert retrieved_entry is not None
    
    assert retrieved_entry.liters == 50.5
    assert retrieved_entry.distance == 450.0
    assert round(retrieved_entry.total_cost, 2) == 78.28
    assert round(retrieved_entry.km_per_liter, 2) == 8.91
    
    assert isinstance(retrieved_entry, FuelEntryDB)

def test_read_nonexistent_entry():
    """Tests attempting to read an ID that does not exist."""
    assert read_entry(999) is None

def test_update_entry():
    """Tests updating an existing entry."""
    
    original_entry = insert_entry(VALID_CREATE_DATA)
    assert original_entry is not None
    
    # 2. Define update data (FIX: Must use FuelEntryUpdate, not FuelEntryCreate)
    update_data = FuelEntryUpdate(
        date="2025-01-01",
        liters=60.0,
        price_per_liter=2.0,
        distance=600.0,
        notes="Updated notes"
    )
    
    # 3. Update the entry
    updated_entry = update_entry(original_entry.id, update_data)
    assert updated_entry is not None
    
    # 4. Verify updated fields and new calculations
    assert updated_entry.id == original_entry.id
    assert updated_entry.liters == 60.0
    assert updated_entry.date == "2025-01-01"
    assert updated_entry.total_cost == 120.0
    assert updated_entry.km_per_liter == 10.0

def test_delete_entry():
    """Tests deleting an existing entry."""
    
    inserted_entry = insert_entry(VALID_CREATE_DATA)
    assert inserted_entry is not None
    
    success = delete_entry(inserted_entry.id)
    assert success is True
    
    assert read_entry(inserted_entry.id) is None

def test_delete_nonexistent_entry():
    """Tests attempting to delete a non-existent entry."""
    assert delete_entry(999) is False

def test_insert_and_list_multiple():
    """
    Tests inserting multiple entries and retrieving them all 
    using the new processed list function.
    """
    
    insert_entry(VALID_CREATE_DATA)
    insert_entry(ANOTHER_CREATE_DATA)
    
    # List the processed entries (Calls the correct new function)
    entries = get_all_entries_processed() 
    
    assert len(entries) == 2
    
    # Entry 2: (45.6L, 785km) -> km/L = 17.22
    entry_a = entries[0]
    assert entry_a.distance == 785.0
    assert round(entry_a.km_per_liter, 2) == 17.21
    assert isinstance(entry_a, FuelEntryDB)

    # Entry 1: (50.5L, 450km) -> km/L = 8.91
    entry_b = entries[1]
    assert entry_b.distance == 450.0
    assert round(entry_b.km_per_liter, 2) == 8.91
    assert isinstance(entry_b, FuelEntryDB)

def test_get_all_entries_raw():
    """Tests the helper function used for overall stats calculation."""
    insert_entry(VALID_CREATE_DATA)
    insert_entry(ANOTHER_CREATE_DATA)