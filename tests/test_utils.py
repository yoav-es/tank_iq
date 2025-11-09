# tests/test_utils.py

import pytest
from app.utils import calculate_entry_stats, get_overall_stats
from app.models import OverallStats

# --- Test Data ---

# Data for individual entry test
LITERS = 50.0
PRICE = 1.50
DISTANCE = 750.0

# Data for overall stats test
ENTRY_LIST_DATA = [
    # Entry 1: 50L, 700km. Cost: 50*7.2=360. km/L: 700/50=14.0
    {'liters': 50.0, 'price_per_liter': 7.2, 'distance': 700.0},
    # Entry 2: 45.6L, 785km. Cost: 45.6*7.2=328.32. km/L: 785/45.6=17.21
    {'liters': 45.6, 'price_per_liter': 7.2, 'distance': 785.0},
]

# --- Tests for calculate_entry_stats ---

def test_calculate_entry_stats_normal():
    """Tests calculation of cost and km/L for a standard entry."""
    stats = calculate_entry_stats(LITERS, PRICE, DISTANCE)

    # Expected: Total Cost (50 * 1.5) = 75.0
    # Expected: km/L (750 / 50) = 15.0
    
    assert stats['total_cost'] == 75.0
    assert stats['km_per_liter'] == 15.0

def test_calculate_entry_stats_zero_liters():
    """Tests calculation when liters is zero (to avoid division by zero)."""
    stats = calculate_entry_stats(0.0, PRICE, DISTANCE)
    assert stats['total_cost'] == 0.0
    assert stats['km_per_liter'] == 0.0

def test_calculate_entry_stats_zero_distance():
    """Tests calculation when distance is zero."""
    stats = calculate_entry_stats(LITERS, PRICE, 0.0)
    assert stats['total_cost'] == 75.0
    assert stats['km_per_liter'] == 0.0 # 0 / 50 = 0.0

# --- Tests for get_overall_stats ---

def test_get_overall_stats_multiple_entries():
    """Tests overall stats calculation with multiple entries."""
    stats_model = get_overall_stats(ENTRY_LIST_DATA)
    
    # Expected Totals:
    # Total Liters: 50.0 + 45.6 = 95.6
    # Total Distance: 700.0 + 785.0 = 1485.0
    # Total Cost: 360.0 + 328.32 = 688.32
    # Avg km/L: 1485.0 / 95.6 = 15.5334...
    
    assert isinstance(stats_model, OverallStats)
    assert stats_model.entry_count == 2
    assert stats_model.total_liters == 95.6
    assert stats_model.total_distance == 1485.0
    assert stats_model.total_cost == 688.32
    
    # Check the key is correct and rounded to 2 places (15.53)
    assert stats_model.average_km_per_liter == 15.53

def test_get_overall_stats_empty_list():
    """Tests overall stats calculation with an empty list."""
    stats_model = get_overall_stats([])
    
    # All values should be zero
    assert isinstance(stats_model, OverallStats)
    assert stats_model.entry_count == 0
    assert stats_model.total_liters == 0.0
    assert stats_model.total_distance == 0.0
    assert stats_model.total_cost == 0.0
    assert stats_model.average_km_per_liter == 0.0