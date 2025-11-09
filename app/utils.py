# app/utils.py

from typing import List, Dict, Any
from .models import OverallStats # Import the model for correct type hinting

def calculate_entry_stats(liters: float, price_per_liter: float, distance: float) -> Dict[str, float]:
    """Calculates total cost and km/liter for a single entry."""
    total_cost = liters * price_per_liter
    
    # Calculate km_per_liter (km/L)
    if liters > 0:
        km_per_liter = distance / liters
    else:
        km_per_liter = 0.0
        
    return {
        "total_cost": round(total_cost, 2),
        "km_per_liter": round(km_per_liter, 2)
    }

def get_overall_stats(entries: List[Dict[str, Any]]) -> OverallStats:
    """Calculates overall statistics, including average km/liter."""
    
    # 1. Initialize cumulative totals
    total_distance = sum(entry['distance'] for entry in entries)
    total_liters = sum(entry['liters'] for entry in entries)
    total_cost = sum(entry['liters'] * entry['price_per_liter'] for entry in entries)
    entry_count = len(entries)
    
    # 2. Calculate average km/liter
    if total_liters > 0:
        # Average km/liter is total distance divided by total liters
        average_km_per_liter = total_distance / total_liters
    else:
        average_km_per_liter = 0.0
    
    # 3. Return the OverallStats model, ensuring correct field names
    stats_data = {
        "total_distance": round(total_distance, 2),
        "total_liters": round(total_liters, 2),
        "total_cost": round(total_cost, 2),
        "entry_count": entry_count,
        # FINAL METRIC FIX: Only use the requested average_km_per_liter key
        "average_km_per_liter": round(average_km_per_liter, 2),
    }

    # Validate and return the Pydantic model
    return OverallStats.model_validate(stats_data)