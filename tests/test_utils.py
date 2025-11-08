# tests/test_utils.py

import pytest
import unittest.mock # Still needed for patching external modules/libraries
from app.utils import calculate_l_per_km, get_overall_stats

# --- 1. Test Core Calculation (calculate_l_per_km) ---

def test_l_per_km_standard():
    """Tests the basic L/km calculation: 40 liters / 500 km = 0.08 L/km."""
    assert calculate_l_per_km(40.0, 500.0) == 0.08

def test_l_per_km_precision():
    """Tests that the calculation maintains the required precision (6 decimal places)."""
    # 90 liters / 1100 km ≈ 0.08181818...
    assert calculate_l_per_km(90.0, 1100.0) == pytest.approx(0.081818)

def test_l_per_km_zero_distance():
    """Tests handling for zero or negative distance driven."""
    assert calculate_l_per_km(10.0, 0.0) == 0.0
    assert calculate_l_per_km(10.0, -100.0) == 0.0

# --- 2. Test Aggregated Stats (get_overall_stats) ---

# Mock data simulating the dictionary/Row objects returned by the database
MOCK_ENTRIES_DATA = [
    {'liters': 40.0, 'price_per_liter': 1.50, 'distance': 500.0},
    {'liters': 50.0, 'price_per_liter': 1.60, 'distance': 600.0},
]

@unittest.mock.patch('app.database.list_entries')
def test_get_overall_stats_with_data(mock_list_entries):
    """Tests stats calculation using mocked database results."""
    
    # Configure the mock to return the test data
    mock_list_entries.return_value = MOCK_ENTRIES_DATA
    
    stats = get_overall_stats()
    
    # Verification of calculated values:
    # Total cost: (40*1.5) + (50*1.6) = 140.0
    # Overall L/km: 90.0 / 1100.0 ≈ 0.081818
    # Avg Price/L: 140.0 / 90.0 ≈ 1.55555...

    assert stats['total_entries'] == 2
    assert stats['total_liters'] == 90.0
    assert stats['total_cost'] == 140.0
    assert stats['overall_l_per_km'] == pytest.approx(0.081818)
    assert stats['avg_price_per_liter'] == pytest.approx(1.5556)

@unittest.mock.patch('app.database.list_entries', return_value=[])
def test_get_overall_stats_empty(mock_list_entries):
    """Tests stats calculation when no entries exist."""
    stats = get_overall_stats()
    assert stats['total_entries'] == 0
    assert stats['overall_l_per_km'] == 0.0
    assert stats['total_cost'] == 0.0