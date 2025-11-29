"""
TankIQ Utilities Tests

This module contains unit tests for helper functions in app/utils.py.
It verifies calculations for individual entries and aggregated overall
statistics using pytest.
"""

import pytest
import logging
from app.utils import calculate_entry_stats, get_overall_stats
from app.models import OverallStats
from app.utils import get_best_efficiency
from app.utils import convert_entries_to_csv
from app.models import TimePeriodStats

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
    """Verify calculation of cost and km/L for different scenarios."""
    stats = calculate_entry_stats(liters, price, distance)
    assert stats["total_cost"] == pytest.approx(expected_cost)
    assert stats["km_per_liter"] == pytest.approx(expected_kmpl)

# --- Tests for get_overall_stats ---

@pytest.mark.parametrize("entries, expected_count, expected_liters, expected_distance, expected_cost, expected_kmpl", [
    (ENTRY_LIST_DATA, 2, 95.6, 1485.0, 688.32, 15.53),  # multiple entries
    ([], 0, 0.0, 0.0, 0.0, 0.0),                       # empty list
])
def test_get_overall_stats(entries, expected_count, expected_liters, expected_distance, expected_cost, expected_kmpl):
    """Verify overall stats calculation with multiple entries and empty list."""
    stats_model = get_overall_stats(entries)
    assert isinstance(stats_model, OverallStats)
    assert stats_model.entry_count == expected_count
    assert stats_model.total_liters == pytest.approx(expected_liters)
    assert stats_model.total_distance == pytest.approx(expected_distance)
    assert stats_model.total_cost == pytest.approx(expected_cost)
    assert stats_model.average_km_per_liter == pytest.approx(expected_kmpl, rel=1e-2)


def test_get_best_efficiency_returns_highest_kmpl():
    """Verify that get_best_efficiency returns the highest km/L value."""
    period_stats = [
        TimePeriodStats(
            period_label="2024-01",
            total_liters=50.0,
            total_cost=100.0,
            total_distance=600.0,
            count=1,
            average_km_per_liter=12.0,
            average_cost_per_liter=2.0,
        ),
        TimePeriodStats(
            period_label="2024-02",
            total_liters=40.0,
            total_cost=90.0,
            total_distance=620.0,
            count=1,
            average_km_per_liter=15.5,
            average_cost_per_liter=2.25,
        ),
        TimePeriodStats(
            period_label="2024-03",
            total_liters=45.0,
            total_cost=95.0,
            total_distance=630.0,
            count=1,
            average_km_per_liter=14.0,
            average_cost_per_liter=2.1,
        ),
    ]
    best = get_best_efficiency(period_stats)
    assert best == 15.5


def test_convert_entries_to_csv_contains_expected_headers_and_values():
    """Verify that convert_entries_to_csv produces valid CSV with headers and entry values."""
    entries = [
        {"id": 1, "date": "2024-11-01", "liters": 50.0, "price_per_liter": 1.5,
         "distance": 800.0, "notes": "Trip"}
    ]
    csv_data = convert_entries_to_csv(entries).replace("\r\n", "\n")
    assert "id,date,liters,price_per_liter,distance,notes" in csv_data
    assert "1,2024-11-01,50.0,1.5,800.0,Trip" in csv_data

def test_get_overall_stats_logs_warning_for_unrealistic_cost(caplog):
    """Verify that get_overall_stats logs a warning when average cost per liter exceeds threshold."""
    high_cost_entries = [
        {"liters": 10.0, "price_per_liter": 25.0, "distance": 100.0},  # cost per liter > 20
    ]
    with caplog.at_level(logging.WARNING):
        stats_model = get_overall_stats(high_cost_entries)
    assert "Average cost per liter looks unrealistic" in caplog.text
    assert stats_model.average_cost_per_liter > 20