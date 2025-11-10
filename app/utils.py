import logging
from typing import List, Dict, Any
from .models import OverallStats # <-- FIX: Import OverallStats model

# --- 1. LOGGING SETUP ---
logger = logging.getLogger(__name__)
# ------------------------

# --- 2. Helper Functions ---

def calculate_entry_stats(liters: float, price_per_liter: float, distance: float) -> Dict[str, float]:
    """Calculates the total cost and fuel efficiency (km/L) for a single entry."""
    total_cost = liters * price_per_liter
    
    # Avoid division by zero if distance is 0
    km_per_liter = distance / liters if liters else 0.0
    
    return {
        "total_cost": round(total_cost, 2),
        "km_per_liter": round(km_per_liter, 2)
    }

# FIX: Return type changed to OverallStats to satisfy unit tests.
def get_overall_stats(entries_raw: List[Dict[str, Any]]) -> OverallStats:
    """
    Calculates overall statistics (totals and averages) from the raw list of entries.
    """
    entry_count = len(entries_raw) 

    if not entries_raw:
        logger.warning("Attempted to calculate overall statistics with an empty dataset.")
        stats = {
            "total_distance": 0.0,
            "total_liters": 0.0,
            "total_cost": 0.0,
            "entry_count": 0, 
            "average_km_per_liter": 0.0
        }
        # FIX: Validate and return the Pydantic model
        return OverallStats.model_validate(stats)

    # 1. Sum up all raw values
    total_distance = sum(entry['distance'] for entry in entries_raw)
    total_liters = sum(entry['liters'] for entry in entries_raw)
    total_cost = sum(entry['liters'] * entry['price_per_liter'] for entry in entries_raw)

    # 2. Calculate global average efficiency
    average_km_per_liter = total_distance / total_liters if total_liters else 0.0

    stats = {
        "total_distance": round(total_distance, 2),
        "total_liters": round(total_liters, 2),
        "total_cost": round(total_cost, 2),
        "entry_count": entry_count, 
        "average_km_per_liter": round(average_km_per_liter, 2)
    }

    # INFO Log: Confirm stats generation
    logger.info("Overall statistics calculated successfully.")
    
    # FIX: Validate and return the Pydantic model
    return OverallStats.model_validate(stats)