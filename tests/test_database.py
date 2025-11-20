import os
import sqlite3
import pytest
from fastapi.testclient import TestClient

from app.server import app
from app.database import DATABASE_NAME, init_db

client = TestClient(app)


# --- Fixtures and Setup ---
@pytest.fixture(autouse=True, scope="module")
def setup_db():
    """Setup and teardown for API tests using a clean database."""
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

    init_db()

    conn = sqlite3.connect(DATABASE_NAME)
    conn.execute("DELETE FROM fuel_entries")
    conn.commit()
    conn.close()

    yield

    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)


@pytest.fixture(autouse=True)
def clean_entries():
    """Clear entries between individual tests."""
    conn = sqlite3.connect(DATABASE_NAME)
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


def test_create_entry():
    """POST /entries/ creates a new entry with calculated fields."""
    response = client.post("/entries/", json=ENTRY_1)
    assert response.status_code == 201

    data = response.json()
    assert data["id"] == 1
    assert data["liters"] == 50.0
    assert data["total_cost"] == 75.0  # 50 * 1.5
    assert data["km_per_liter"] == 16.0  # 800 / 50


def test_list_entries_with_stats():
    """GET /entries/ returns entries and correct overall statistics."""
    client.post("/entries/", json=ENTRY_1)
    client.post("/entries/", json=ENTRY_2)

    response = client.get("/entries/")
    assert response.status_code == 200
    data = response.json()

    assert len(data["entries"]) == 2
    stats = data["overall_stats"]

    assert stats["entry_count"] == 2
    assert stats["total_liters"] == 75.0
    assert stats["total_distance"] == 1100.0
    assert stats["total_cost"] == 115.0
    assert stats["average_km_per_liter"] == 14.67


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
    assert overall["average_km_per_liter"] == 14.40

    monthly = sorted(data["monthly_stats"], key=lambda x: x["period_label"])
    assert len(monthly) == 3
    assert monthly[0]["period_label"] == "2023-11"
    assert monthly[1]["period_label"] == "2024-11"
    assert monthly[2]["period_label"] == "2024-12"

    yearly = sorted(data["yearly_stats"], key=lambda x: x["period_label"])
    assert len(yearly) == 2
    assert yearly[0]["period_label"] == "2023"
    assert yearly[1]["period_label"] == "2024"