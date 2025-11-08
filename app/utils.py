# app/utils.py

from typing import Dict, Union
# Import the database function to fetch the raw data
from app import database 

# --- Constants ---
LITERS_KEY = 'liters'
PRICE_KEY = 'price_per_liter'
DISTANCE_KEY = 'distance'

# --- Core Calculations ---

def calculate_l_per_km(liters: float, distance_km: float) -> float:
    """
    Calculates fuel efficiency in Liters per Kilometer (L/km).

    Args:
        liters (float): The amount of fuel used.
        distance_km (float): The distance traveled in kilometers.

    Returns:
        float: Fuel efficiency (L/km) rounded to 6 decimal places. Returns 0.0 if distance is zero or negative.
    """
    if distance_km <= 0:
        return 0.0
    # maybe allow switching 
    # Formula: Liters / Distance in km
    efficiency = liters / distance_km
    # Using 6 decimal places to maintain precision for a small value like L/km
    return round(efficiency, 6)


def get_overall_stats() -> Dict[str, Union[float, int]]:
    """
    Calculates and returns overall aggregated fuel statistics from all entries.

    Metrics include total consumption, total cost, and overall average efficiency (L/km).

    Returns:
        Dict[str, Union[float, int]]: A dictionary containing key metrics.
    """
    # 1. Fetch raw data (list of sqlite3.Row objects)
    entries = database.list_entries()
    
    if not entries:
        return {
            "total_entries": 0,
            "total_distance_km": 0.0,
            "total_liters": 0.0,
            "total_cost": 0.0,
            "avg_price_per_liter": 0.0,
            "overall_l_per_km": 0.0  # Renamed key
        }

    # 2. Aggregate raw data
    total_liters = sum(e[LITERS_KEY] for e in entries)
    total_distance_km = sum(e[DISTANCE_KEY] for e in entries)
    total_cost = sum(e[LITERS_KEY] * e[PRICE_KEY] for e in entries)
    
    # 3. Calculate derived stats
    
    # Calculate weighted average price per liter (Total Cost / Total Liters)
    avg_price_per_liter = total_cost / total_liters if total_liters >0 else 0.0

    # Calculate overall fuel efficiency using the L/km function
    overall_l_per_km = calculate_l_per_km(total_liters, total_distance_km)

    # 4. Return results
    return {
        "total_entries": len(entries),
        "total_distance_km": round(total_distance_km, 2),
        "total_liters": round(total_liters, 2),
        "total_cost": round(total_cost, 2),
        "avg_price_per_liter": round(avg_price_per_liter, 4),
        "overall_l_per_km": overall_l_per_km, # Updated key and value
    }