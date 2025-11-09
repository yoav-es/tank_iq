# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
import sqlite3
import os

# Import the application instance and init_db function
from app.server import app 
from app.database import DATABASE_NAME, init_db # 🛑 IMPORT init_db

client = TestClient(app)

# --- Fixtures and Setup ---

@pytest.fixture(autouse=True, scope="module")
def setup_db():
    """Setup and Teardown for API tests using a clean database."""
    # Ensure the database is clean before running the suite
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)
    
    # 🛑 FIX: Explicitly initialize the database table for the test environment
    init_db() 
    
    # We rely on init_db() being called when the app starts, 
    # but clear the table before each test run.
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM fuel_entries")
    conn.commit()
    conn.close()
    
    yield # Run tests
    
    # Clean up after all tests
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

@pytest.fixture(autouse=True)
def clean_entries():
    """Clears entries between individual tests."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM fuel_entries")
    conn.commit()
    conn.close()

# --- Test Data (Rest of the file remains the same) ---

ENTRY_1 = {
    "date": "2024-11-01", 
    "liters": 50.0, 
    "price_per_liter": 1.5, 
    "distance": 800.0, 
    "notes": "Long trip"
}

ENTRY_2 = {
    "date": "2024-11-02", 
    "liters": 25.0, 
    "price_per_liter": 1.6, 
    "distance": 300.0, 
    "notes": "Short trip"
}

# --- Tests (Rest of the tests remain the same) ---

def test_list_entries_empty():
    """Tests the GET /entries/ endpoint when the database is empty."""
    response = client.get("/entries/")
    assert response.status_code == 200
    data = response.json()
    
    assert data["entries"] == []
    # Verify overall_stats structure for empty case
    stats = data["overall_stats"]
    assert stats["entry_count"] == 0
    assert stats["total_distance"] == 0.0
    assert stats["average_km_per_liter"] == 0.0

def test_create_entry():
    """Tests the POST /entries/ endpoint."""
    response = client.post("/entries/", json=ENTRY_1)
    assert response.status_code == 201
    
    data = response.json()
    assert data["id"] == 1
    assert data["liters"] == 50.0
    
    # Verify calculated fields on creation
    assert data["total_cost"] == 75.0 # 50 * 1.5
    assert data["km_per_liter"] == 16.0 # 800 / 50

def test_read_entry():
    """Tests the GET /entries/{entry_id} endpoint."""
    
    # 1. Create an entry
    post_response = client.post("/entries/", json=ENTRY_1)
    entry_id = post_response.json()["id"]
    
    # 2. Read the entry
    get_response = client.get(f"/entries/{entry_id}")
    assert get_response.status_code == 200
    
    data = get_response.json()
    assert data["id"] == entry_id
    assert data["distance"] == 800.0
    assert data["km_per_liter"] == 16.0 # Verify calculated field

def test_read_nonexistent_entry():
    """Tests reading an entry that does not exist."""
    response = client.get("/entries/999")
    assert response.status_code == 404

def test_update_entry():
    """Tests the PUT /entries/{entry_id} endpoint."""
    
    # 1. Create original entry
    post_response = client.post("/entries/", json=ENTRY_1)
    entry_id = post_response.json()["id"]
    
    # 2. Define update payload (change liters and distance to change metrics)
    update_payload = {
        "date": "2024-11-03", 
        "liters": 100.0, 
        "price_per_liter": 2.0, 
        "distance": 1000.0, 
        "notes": "Updated long trip"
    }
    
    # 3. Update
    put_response = client.put(f"/entries/{entry_id}", json=update_payload)
    assert put_response.status_code == 200
    
    data = put_response.json()
    assert data["liters"] == 100.0
    # Verify new calculated fields
    assert data["total_cost"] == 200.0 # 100 * 2.0
    assert data["km_per_liter"] == 10.0 # 1000 / 100

def test_delete_entry():
    """Tests the DELETE /entries/{entry_id} endpoint."""
    
    # 1. Create entry
    post_response = client.post("/entries/", json=ENTRY_1)
    entry_id = post_response.json()["id"]
    
    # 2. Delete
    delete_response = client.delete(f"/entries/{entry_id}")
    assert delete_response.status_code == 204
    
    # 3. Verify deletion
    get_response = client.get(f"/entries/{entry_id}")
    assert get_response.status_code == 404

def test_list_entries_with_stats():
    """Tests listing entries and verifies overall statistics."""
    
    # 1. Create two entries
    client.post("/entries/", json=ENTRY_1)
    client.post("/entries/", json=ENTRY_2)
    
    # 2. List entries
    response = client.get("/entries/")
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["entries"]) == 2 # Check list size
    
    # Totals: 
    # Total Liters: 50.0 + 25.0 = 75.0
    # Total Distance: 800.0 + 300.0 = 1100.0
    # Total Cost: (50*1.5) + (25*1.6) = 75 + 40 = 115.0
    # Avg km/L: 1100.0 / 75.0 = 14.666... -> 14.67
    
    stats = data["overall_stats"]
    assert stats["entry_count"] == 2
    assert stats["total_liters"] == 75.0
    assert stats["total_distance"] == 1100.0
    assert stats["total_cost"] == 115.0
    assert stats["average_km_per_liter"] == 14.67 # Verify correct calculated metric