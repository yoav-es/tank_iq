# app/utils.py
import logging
import csv
from io import StringIO
from typing import List, Dict, Any, Sequence

from .models import OverallStats, TimePeriodStats

logger = logging.getLogger(__name__)


def calculate_entry_stats(
    liters: float,
    price_per_liter: float,
    distance: float,
) -> Dict[str, float]:
    """Calculate total cost and fuel efficiency (km/L) for a single entry."""
    total_cost = liters * price_per_liter
    km_per_liter = distance / liters if liters else 0.0

    return {
        "total_cost": round(total_cost, 2),
        "km_per_liter": round(km_per_liter, 2),
    }


def get_overall_stats(entries_raw: List[Dict[str, Any]]) -> OverallStats:
    """
    Calculate overall statistics (totals and averages) from raw entries.

    Returns:
        OverallStats: Pydantic model with totals and averages.
    """
    entry_count = len(entries_raw)

    if not entries_raw:
        logger.warning(
            "Attempted to calculate overall statistics with an empty dataset."
        )
        return OverallStats(
            total_distance=0.0,
            total_liters=0.0,
            total_cost=0.0,
            entry_count=0,
            average_km_per_liter=0.0,
            average_cost_per_liter=0.0,
            best_month_efficiency=0.0,
            best_year_efficiency=0.0,
        )

    total_liters = sum(entry["liters"] for entry in entries_raw)
    total_distance = sum(entry["distance"] for entry in entries_raw)
    total_cost = sum(
        entry["liters"] * entry["price_per_liter"] for entry in entries_raw
    )

    average_km_per_liter = total_distance / total_liters if total_liters else 0.0
    average_cost_per_liter = total_cost / total_liters if total_liters else 0.0

    stats = {
        "total_distance": round(total_distance, 2),
        "total_liters": round(total_liters, 2),
        "total_cost": round(total_cost, 2),
        "entry_count": entry_count,
        "average_km_per_liter": round(average_km_per_liter, 2),
        "average_cost_per_liter": round(average_cost_per_liter, 2),
        # placeholders, filled later in /stats endpoint
        "best_month_efficiency": 0.0,
        "best_year_efficiency": 0.0,
    }

    logger.info("Overall statistics calculated successfully.")
    return OverallStats(**stats)


def get_best_efficiency(period_stats: Sequence[TimePeriodStats], label: str) -> float:
    """
    Return the highest km/L across a given period (month or year).

    Args:
        period_stats (Sequence[TimePeriodStats]): List of monthly or yearly stats.
        label (str): Label type ("month" or "year"), kept for compatibility.

    Returns:
        float: Best efficiency (km/L). Returns 0.0 if no stats available.
    """
    if not period_stats:
        return 0.0
    return max(p.average_km_per_liter for p in period_stats)


def convert_entries_to_csv(entries: List[Dict[str, Any]]) -> str:
    """Convert a list of raw fuel entry dictionaries into a CSV string."""
    if not entries:
        logger.warning("Attempted to convert an empty list to CSV.")
        return "No data to export"

    output = StringIO()

    fieldnames = ["date", "liters", "price_per_liter", "distance", "notes"]
    if "id" in entries[0]:
        fieldnames.insert(0, "id")

    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()

    for entry in entries:
        writer.writerow(entry)

    csv_string = output.getvalue()
    logger.info("Successfully converted %d entries to CSV format.", len(entries))

    return csv_string