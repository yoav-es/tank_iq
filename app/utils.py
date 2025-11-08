# app/utils.py

from typing import Dict, Any, List
from decimal import Decimal, ROUND_HALF_UP 

def calculate_l_per_km(liters: float, distance: float) -> float:
    """Calculates fuel efficiency in Liters per Kilometer (L/km), rounded to 2 decimal places."""
    if distance <= 0:
        return 0.0
    
    efficiency = liters / distance
    return round(efficiency, 2)

def calculate_total_cost(liters: float, price_per_liter: float) -> float:
    """
    Calculates the total cost of a fuel entry using the Decimal module for guaranteed 
    2-decimal precision (currency).
    """
    # Convert float inputs to Decimal using str() for accurate representation
    liters_dec = Decimal(str(liters))
    price_dec = Decimal(str(price_per_liter))
    
    # Perform multiplication
    total_cost_dec = liters_dec * price_dec
    
    # Round to 2 decimal places (cents)
    rounded_cost_dec = total_cost_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Convert back to float for API response consistency
    return float(rounded_cost_dec)

def calculate_entry_stats(liters: float, price_per_liter: float, distance: float) -> Dict[str, Any]:
    """Helper to calculate all derived fields for a single entry."""
    return {
        "l_per_km": calculate_l_per_km(liters, distance),
        "total_cost": calculate_total_cost(liters, price_per_liter)
    }

def get_overall_stats(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculates overall statistics (total distance, total liters, total cost, average consumption) 
    from a list of raw entry dictionaries returned by the database.
    """
    if not entries:
        return {
            "total_distance_km": 0.0,
            "total_liters": 0.0,
            "total_cost": 0.0,
            "average_l_per_100km": 0.0
        }

    total_liters = sum(e['liters'] for e in entries)
    total_distance_km = sum(e['distance'] for e in entries)
    
    # Perform cost aggregation using Decimal for precision (best practice)
    # 🛑 FIX: Use start=Decimal(0) to ensure the result is always a Decimal, avoiding the quantize error.
    total_cost_dec = sum((
            Decimal(str(e['liters'])) * Decimal(str(e['price_per_liter'])) 
            for e in entries
        ), start=Decimal(0)) # <--- SYNTAX FIXED
    
    # Round the total cost down to 2 decimals for output
    total_cost = float(total_cost_dec.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))
    
    
    # Calculate average consumption (L/100km)
    if total_distance_km > 0:
        # L/100km calculation and rounding to 2 decimal places
        average_l_per_100km = (total_liters / total_distance_km) * 100
        average_l_per_100km = round(average_l_per_100km, 2)
    else:
        average_l_per_100km = 0.0

    return {
        "total_distance_km": round(total_distance_km, 1), # Keep distance at 1 decimal place
        "total_liters": round(total_liters, 2),
        "total_cost": total_cost,
        "average_l_per_100km": average_l_per_100km
    }