# tests/test_database.py
import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.server import app
from app.database import DATABASE_PATH, init_db

client = TestClient(app)

# --- Fixtures and Setup ---
@pytest.fixture(autouse=True, scope="module")
def setup_db():
    """Setup and teardown for API tests using a clean database file."""
    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

    init_db()

    yield

    if os.path.exists(DATABASE_PATH):
        os.remove(DATABASE_PATH)

@pytest.fixture(autouse=True)
def clean_entries():
    """Clear entries between individual tests for isolation."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("DELETE FROM fuel_entries")
    conn.commit()
    conn.close()

# --- Test Data ---
ENTRY_1 = {
    "date": "2024-11-01",
    "liters": 50.0,
    "price_per_liter": 1.5,
    "distance": 800.0,
    "notes": "Long trip (2024 Nov)",
}
ENTRY_2 = {
    "date": "2024-11-02",
    "liters": 25.0,
    "price_per_liter": 1.6,
    "distance": 300.0,
    "notes": "Short trip (2024 Nov)",
}
ENTRY_3 = {
    "date": "2023-11-15",
    "liters": 10.0,
    "price_per_liter": 1.0,
    "distance": 100.0,
    "notes": "Annual entry (2023 Nov)",
}
ENTRY_4 = {
    "date": "2024-12-05",
    "liters": 40.0,
    "price_per_liter": 2.0,
    "distance": 600.0,
    "notes": "Next month (2024 Dec)",
}
ALL_ENTRIES = [ENTRY_1, ENTRY_2, ENTRY_3, ENTRY_4]

# --- Tests ---
def test_list_entries_empty():
    """GET /entries/ returns empty list and zeroed stats when DB is empty."""
    response = client.get("/entries/")
    assert response.status_code == 200
    data = response.json()
    assert data["entries"] == []
    stats = data["overall_stats"]
    assert stats["entry_count"] == 0
    assert stats["total_distance"] == 0.0
    assert stats["average_km_per_liter"] == 0.0

@pytest.mark.parametrize("entry,expected_cost,expected_kmpl", [
    (ENTRY_1, 75.0, 16.0),
    (ENTRY_2, 40.0, 12.0),
    (ENTRY_3, 10.0, 10.0),
    (ENTRY_4, 80.0, 15.0),
])
def test_create_entry_parametrized(entry, expected_cost, expected_kmpl):
    """POST /entries/ creates entries with calculated fields."""
    response = client.post("/entries/", json=entry)
    assert response.status_code == 201
    data = response.json()
    assert data["liters"] == entry["liters"]
    assert data["total_cost"] == pytest.approx(expected_cost)
    assert data["km_per_liter"] == pytest.approx(expected_kmpl)

@pytest.mark.parametrize("entries,expected_count,expected_liters,expected_distance,expected_cost,expected_kmpl", [
    ([ENTRY_1, ENTRY_2], 2, 75.0, 1100.0, 115.0, 14.67),
    (ALL_ENTRIES, 4, 125.0, 1800.0, 205.0, 14.40),
])
def test_stats_counts(entries, expected_count, expected_liters, expected_distance, expected_cost, expected_kmpl):
    """GET /stats/ returns correct overall statistics for different sets of entries."""
    for e in entries:
        client.post("/entries/", json=e)
    response = client.get("/stats/")
    assert response.status_code == 200
    overall = response.json()["overall_stats"]
    assert overall["entry_count"] == expected_count
    assert overall["total_liters"] == pytest.approx(expected_liters)
    assert overall["total_distance"] == pytest.approx(expected_distance)
    assert overall["total_cost"] == pytest.approx(expected_cost)
    assert overall["average_km_per_liter"] == pytest.approx(expected_kmpl, rel=1e-2)

def test_get_detailed_stats_empty():
    """GET /stats/ returns zeroed stats when DB is empty."""
    response = client.get("/stats/")
    assert response.status_code == 200
    data = response.json()
    overall = data["overall_stats"]
    assert overall["entry_count"] == 0
    assert overall["total_liters"] == 0.0
    assert data["monthly_stats"] == []
    assert data["yearly_stats"] == []

def test_get_detailed_stats_multi_period():
    """GET /stats/ returns correct monthly and yearly aggregations."""
    for entry in ALL_ENTRIES:
        client.post("/entries/", json=entry)
    response = client.get("/stats/")
    assert response.status_code == 200
    data = response.json()
    overall = data["overall_stats"]
    assert overall["entry_count"] == 4
    assert overall["total_liters"] == 125.0
    assert overall["total_distance"] == 1800.0
    assert overall["total_cost"] == 205.0
    assert overall["average_km_per_liter"] == pytest.approx(14.40, rel=1e-2)

    monthly = sorted(data["monthly_stats"], key=lambda x: x["period_label"])
    assert [m["period_label"] for m in monthly] == ["2023-11", "2024-11", "2024-12"]

    yearly = sorted(data["yearly_stats"], key=lambda x: x["period_label"])
    assert [y["period_label"] for y in yearly] == ["2023", "2024"]