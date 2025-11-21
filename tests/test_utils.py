# tests/test_utils.py

import pytest
from app.utils import calculate_entry_stats, get_overall_stats
from app.models import OverallStats

# --- Shared Test Data ---
LITERS = 50.0
PRICE = 1.50
DISTANCE = 750.0

ENTRY_LIST_DATA = [
    # Entry 1: 50L, 700km. Cost: 50*7.2=360. km/L: 700/50=14.0
    {"liters": 50.0, "price_per_liter": 7.2, "distance": 700.0},
    # Entry 2: 45.6L, 785km. Cost: 45.6*7.2=328.32. km/L: 785/45.6≈17.21
    {"liters": 45.6, "price_per_liter": 7.2, "distance": 785.0},
]

# --- Tests for calculate_entry_stats ---

@pytest.mark.parametrize("liters, price, distance, expected_cost, expected_kmpl", [
    (LITERS, PRICE, DISTANCE, 75.0, 15.0),   # normal case
    (0.0, PRICE, DISTANCE, 0.0, 0.0),        # zero liters
    (LITERS, PRICE, 0.0, 75.0, 0.0),         # zero distance
])
def test_calculate_entry_stats(liters, price, distance, expected_cost, expected_kmpl):
    """Tests calculation of cost and km/L for different scenarios."""
    stats = calculate_entry_stats(liters, price, distance)
    assert stats["total_cost"] == pytest.approx(expected_cost)
    assert stats["km_per_liter"] == pytest.approx(expected_kmpl)

# --- Tests for get_overall_stats ---

@pytest.mark.parametrize("entries, expected_count, expected_liters, expected_distance, expected_cost, expected_kmpl", [
    (ENTRY_LIST_DATA, 2, 95.6, 1485.0, 688.32, 15.53),  # multiple entries
    ([], 0, 0.0, 0.0, 0.0, 0.0),                       # empty list
])
def test_get_overall_stats(entries, expected_count, expected_liters, expected_distance, expected_cost, expected_kmpl):
    """Tests overall stats calculation with multiple entries and empty list."""
    stats_model = get_overall_stats(entries)
    assert isinstance(stats_model, OverallStats)
    assert stats_model.entry_count == expected_count
    assert stats_model.total_liters == pytest.approx(expected_liters)
    assert stats_model.total_distance == pytest.approx(expected_distance)
    assert stats_model.total_cost == pytest.approx(expected_cost)
    assert stats_model.average_km_per_liter == pytest.approx(expected_kmpl, rel=1e-2)