"""
TankIQ API Tests

This module contains integration tests for the FastAPI endpoints
defined in app/api.py. It verifies CRUD operations, statistics
aggregation, and response validation using pytest and TestClient.
"""

import pytest
from fastapi.testclient import TestClient
import app.database as database

# --- Fixture ---
@pytest.fixture
def client():
    """
    Provide a FastAPI TestClient with a guaranteed schema and clean table.

    Ensures the database schema exists and clears any leftover rows
    before yielding the client for test isolation.
    """
    database.init_db(database.DATABASE_PATH)
    with database.get_db(database.DATABASE_PATH) as conn:
        conn.execute("DELETE FROM fuel_entries")
        conn.commit()

    from app.server import app
    test_client = TestClient(app)
    yield test_client

# --- Test Data ---
ENTRY_1 = {"date": "2024-11-01", "liters": 50.0, "price_per_liter": 1.5, "distance": 800.0, "notes": "Long trip"}
ENTRY_2 = {"date": "2024-11-02", "liters": 25.0, "price_per_liter": 1.6, "distance": 300.0, "notes": "Short trip"}
ENTRY_3 = {"date": "2023-11-15", "liters": 10.0, "price_per_liter": 1.0, "distance": 100.0, "notes": "Annual entry"}
ENTRY_4 = {"date": "2024-12-05", "liters": 40.0, "price_per_liter": 2.0, "distance": 600.0, "notes": "Next month"}
ALL_ENTRIES = [ENTRY_1, ENTRY_2, ENTRY_3, ENTRY_4]

# --- Tests ---

def test_list_entries_empty(client):
    """Verify that /entries returns an empty list and zero stats when no data exists."""
    response = client.get("/entries/")
    assert response.status_code == 200
    data = response.json()
    assert data["entries"] == []
    assert data["overall_stats"]["entry_count"] == 0

@pytest.mark.parametrize("entry", ALL_ENTRIES)
def test_create_entry_parametrized(client, entry):
    """Verify that creating entries returns correct fields and derived stats."""
    response = client.post("/entries/", json=entry)
    assert response.status_code == 201
    data = response.json()
    assert data["liters"] == entry["liters"]
    assert data["price_per_liter"] == entry["price_per_liter"]
    assert data["distance"] == entry["distance"]
    assert data["total_cost"] == pytest.approx(entry["liters"] * entry["price_per_liter"])
    assert data["km_per_liter"] == pytest.approx(entry["distance"] / entry["liters"])

@pytest.mark.parametrize("entries,expected_count", [
    ([ENTRY_1, ENTRY_2], 2),
    ([ENTRY_1, ENTRY_2, ENTRY_3, ENTRY_4], 4),
])
def test_stats_counts(client, entries, expected_count):
    """Verify that /stats reports correct entry counts after inserts."""
    for e in entries:
        client.post("/entries/", json=e)
    response = client.get("/stats/")
    overall = response.json()["overall_stats"]
    assert overall["entry_count"] == expected_count

def test_get_detailed_stats_empty(client):
    """Verify that /stats returns empty stats when no entries exist."""
    response = client.get("/stats/")
    data = response.json()
    assert data["overall_stats"]["entry_count"] == 0
    assert isinstance(data["monthly_stats"], list)
    assert isinstance(data["yearly_stats"], list)

def test_update_entry(client):
    """Verify that updating an entry modifies fields and recalculates derived stats."""
    response = client.post("/entries/", json=ENTRY_1)
    entry_id = response.json()["id"]

    updated = {**ENTRY_1, "liters": 60.0, "notes": "Updated trip"}
    response = client.put(f"/entries/{entry_id}", json=updated)
    assert response.status_code == 200
    data = response.json()
    assert data["liters"] == 60.0
    assert data["notes"] == "Updated trip"
    assert data["total_cost"] == pytest.approx(60.0 * ENTRY_1["price_per_liter"])
    assert data["km_per_liter"] == pytest.approx(ENTRY_1["distance"] / 60.0, rel=1e-3)

def test_delete_entry(client):
    """Verify that deleting an entry removes it from /entries results."""
    response = client.post("/entries/", json=ENTRY_2)
    entry_id = response.json()["id"]

    response = client.delete(f"/entries/{entry_id}")
    assert response.status_code in (200, 204)

    response = client.get("/entries/")
    data = response.json()
    assert all(e["id"] != entry_id for e in data["entries"])

def test_export_csv_returns_valid_csv(client):
    """Verify that /entries/export/ returns CSV with correct headers and values."""
    # Insert a couple of entries
    client.post("/entries/", json=ENTRY_1)
    client.post("/entries/", json=ENTRY_2)

    response = client.get("/entries/export/")
    assert response.status_code == 200
    csv_text = response.text.replace("\r\n", "\n")

    # Check headers
    assert "id,date,liters,price_per_liter,distance,notes" in csv_text

    # Check that at least one entry row is present
    assert "2024-11-01" in csv_text
    assert "2024-11-02" in csv_text

def test_export_csv_empty_returns_no_data_message(client):
    """Verify that /entries/export/ returns 'No data to export' when no entries exist."""
    response = client.get("/entries/export/")
    assert response.status_code == 200
    assert response.text.strip() == "No data to export"


def test_export_csv_with_date_filters(client):
    """Verify that /entries/export/ respects start_date and end_date filters."""
    # Insert multiple entries
    for e in ALL_ENTRIES:
        client.post("/entries/", json=e)

    # Filter only November 2024 entries
    response = client.get("/entries/export/?start_date=2024-11-01&end_date=2024-11-30")
    assert response.status_code == 200
    csv_text = response.text.replace("\r\n", "\n")

    # Should include ENTRY_1 and ENTRY_2, exclude December and 2023 entries
    assert "2024-11-01" in csv_text
    assert "2024-11-02" in csv_text
    assert "2024-12-05" not in csv_text
    assert "2023-11-15" not in csv_text
