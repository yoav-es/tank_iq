# tests/test_utils.py

import pytest
from app.utils import calculate_l_per_km, calculate_total_cost, calculate_entry_stats, get_overall_stats

# --- 1. Test calculate_l_per_km ---

def test_l_per_km_normal_case():
    """Tests standard L/km calculation with 2 decimal precision."""
    liters = 50.0
    distance = 555.55
    # Expected: 50.0 / 555.55 = 0.0900018... -> rounded to 0.09
    assert calculate_l_per_km(liters, distance) == pytest.approx(0.09) # <-- FIXED EXPECTATION

def test_l_per_km_zero_distance():
    """Tests case where distance is zero (should return 0.0)."""
    assert calculate_l_per_km(50.0, 0.0) == 0.0

def test_l_per_km_near_zero_distance():
    """Tests case with a very small distance."""
    assert calculate_l_per_km(1.0, 0.0001) == 10000.0

def test_l_per_km_high_precision():
    """Tests that the result is rounded to 2 decimal places."""
    liters = 1.0
    distance = 3.0
    # Expected: 1/3 = 0.333333... -> rounded to 0.33
    assert calculate_l_per_km(liters, distance) == pytest.approx(0.33) # <-- FIXED EXPECTATION

# --- 2. Test calculate_total_cost ---

def test_total_cost_simple_case(): # <-- RENAMED FUNCTION
    """Tests standard total cost calculation with simpler values (rounded to 2 decimal places)."""

    # Define the inputs
    liters = 50.0
    price = 2.05
    
    # Expected value: 50.0 * 2.05 = 102.50
    expected_cost = 102.50

    # Assert using the explicit variables
    assert calculate_total_cost(liters, price) == pytest.approx(expected_cost)

def test_total_cost_zero_liters():
    """Tests case where liters is zero."""
    assert calculate_total_cost(0.0, 2.0) == 0.0

def test_total_cost_high_precision():
    """Tests that the result is rounded to 2 decimal places."""
    # Expected: 10.0 * 0.12345 = 1.2345 -> rounded to 1.23
    assert calculate_total_cost(10.0, 0.12345) == pytest.approx(1.23)

# --- 3. Test calculate_entry_stats ---

def test_entry_stats_output():
    """Tests that the helper returns both derived fields correctly."""
    stats = calculate_entry_stats(liters=50.0, price_per_liter=2.0, distance=500.0)
    
    # Check keys
    assert "l_per_km" in stats
    assert "total_cost" in stats
    
    # Check calculated values
    assert stats["l_per_km"] == pytest.approx(0.100) # 3 decimal places
    assert stats["total_cost"] == pytest.approx(100.00)

# --- 4. Test get_overall_stats ---

def test_overall_stats_empty_list():
    """Tests overall stats with an empty entry list."""
    stats = get_overall_stats([])
    assert stats["total_distance_km"] == pytest.approx(0.0)
    assert stats["total_liters"] == pytest.approx(0.0)
    assert stats["average_l_per_100km"] == pytest.approx(0.0)

def test_overall_stats_single_entry():
    """Tests overall stats with a single entry."""
    entries = [{
        "liters": 20.0, 
        "price_per_liter": 2.0, 
        "distance": 200.0
    }]
    stats = get_overall_stats(entries)
    
    assert stats["total_distance_km"] == pytest.approx(200.0)
    assert stats["total_liters"] == pytest.approx(20.0)
    assert stats["total_cost"] == pytest.approx(40.0)
    # Average L/100km: 10.00
    assert stats["average_l_per_100km"] == pytest.approx(10.00)

def test_overall_stats_multiple_entries():
    """Tests overall stats with multiple entries."""
    entries = [
        {"liters": 10.0, "price_per_liter": 1.0, "distance": 100.0},
        {"liters": 20.0, "price_per_liter": 2.0, "distance": 300.0},
        {"liters": 5.0, "price_per_liter": 1.5, "distance": 50.0},
    ]
    stats = get_overall_stats(entries)
    
    # Total Distance: 450.0
    # Total Liters: 35.0
    # Total Cost: 57.5
    # Avg L/100km: 7.777... -> rounded to 7.78
    
    assert stats["total_distance_km"] == pytest.approx(450.0)
    assert stats["total_liters"] == pytest.approx(35.0)
    assert stats["total_cost"] == pytest.approx(57.50)
    assert stats["average_l_per_100km"] == pytest.approx(7.78)