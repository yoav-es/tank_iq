import logging
from typing import List, Dict, Any
from .models import OverallStats
from io import StringIO
import csv

# --- 1. LOGGING SETUP ---
logger = logging.getLogger(__name__)
# ------------------------

# --- 2. Helper Functions ---

def calculate_entry_stats(liters: float, price_per_liter: float, distance: float) -> Dict[str, float]:
    """Calculates the total cost and fuel efficiency (km/L) for a single entry."""
    total_cost = liters * price_per_liter
    
    # Avoid division by zero if liters is 0
    km_per_liter = distance / liters if liters else 0.0
    
    return {
        "total_cost": round(total_cost, 2),
        "km_per_liter": round(km_per_liter, 2)
    }

def get_overall_stats(entries_raw: List[Dict[str, Any]]) -> OverallStats:
    """
    Calculates overall statistics (totals and averages) from the raw list of entries.
    
    Returns:
        An instance of the OverallStats Pydantic model.
    """
    entry_count = len(entries_raw) 
    
    if not entries_raw:
        logger.warning("Attempted to calculate overall statistics with an empty dataset.")
        # Return a zeroed-out model instance for the empty case
        return OverallStats(
            total_distance=0.0,
            total_liters=0.0,
            total_cost=0.0,
            entry_count=0, 
            average_km_per_liter=0.0,
            average_cost_per_liter=0.0 
        ) 

    # 1. Sum up all raw values
    total_liters = sum(entry['liters'] for entry in entries_raw)
    total_distance = sum(entry['distance'] for entry in entries_raw)
    total_cost = sum(entry['liters'] * entry['price_per_liter'] for entry in entries_raw)

    # 2. Calculate global averages
    average_km_per_liter = total_distance / total_liters if total_liters else 0.0
    average_cost_per_liter = total_cost / total_liters if total_liters else 0.0

    stats = {
        "total_distance": round(total_distance, 2),
        "total_liters": round(total_liters, 2),
        "total_cost": round(total_cost, 2),
        "entry_count": entry_count, 
        "average_km_per_liter": round(average_km_per_liter, 2),
        "average_cost_per_liter": round(average_cost_per_liter, 2) 
    }

    logger.info("Overall statistics calculated successfully.")
    
    # CRITICAL FIX: Instantiate and return the Pydantic model
    return OverallStats(**stats)


# --- 3. CSV Conversion Function ---
def convert_entries_to_csv(entries: List[Dict[str, Any]]) -> str:
    """
    Converts a list of raw fuel entry dictionaries into a CSV formatted string.
    """
    if not entries:
        logger.warning("Attempted to convert an empty list to CSV.")
        return "No data to export"

    # Use StringIO to treat a string in memory like a file
    output = StringIO()
    
    # Determine field names (order matters for CSV header)
    fieldnames = ['date', 'liters', 'price_per_liter', 'distance', 'notes']
    
    # Ensure 'id' is included in fieldnames if it's in the entries from the database
    if entries and 'id' in entries[0]:
        fieldnames.insert(0, 'id') 
    
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    
    # Write the header
    writer.writeheader()
    
    # Write the data rows
    for entry in entries:
        writer.writerow(entry)
    
    csv_string = output.getvalue()
    logger.info(f"Successfully converted {len(entries)} entries to CSV format.")
    
    return csv_string