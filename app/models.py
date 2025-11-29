# app/models.py
"""
TankIQ Models Module

This module defines the Pydantic models used for request validation,
database responses, and statistical aggregations. It ensures consistent
schemas across API endpoints and enforces data integrity.
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, field_validator, ConfigDict


# --- 1. Base Model (Shared Fields) ---
class FuelEntryBase(BaseModel):
    """
    Base model containing fields common to all fuel entries.
    """

    date: str
    liters: float
    price_per_liter: float
    distance: float
    notes: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        """
        Validate that the date is in YYYY-MM-DD format.
        """
        try:
            date.fromisoformat(value)
            return value
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format.") from exc

    @field_validator("liters", "price_per_liter", "distance")
    @classmethod
    def validate_non_negative(cls, value: float) -> float:
        """
        Ensure liters, price_per_liter, and distance are non-negative.
        """
        if value < 0:
            raise ValueError("Value must be non-negative.")
        return value

# --- 2. Input/Create/Update Models ---
class FuelEntryCreate(FuelEntryBase):
    """
    Schema for creating a new fuel entry via POST request.
    """
    ...


class FuelEntryUpdate(FuelEntryBase):
    """
    Schema for updating an existing fuel entry via PUT request.
    """
    ...


# --- 3. Database/Output Model (Includes Calculated Fields) ---
class FuelEntryDB(FuelEntryBase):
    """
    Schema for data retrieved from the database and sent as a response.
    Includes the database ID and calculated properties.
    """

    id: int
    total_cost: float
    km_per_liter: float

    model_config = ConfigDict(from_attributes=True)


# --- 4. Overall Stats Model ---
class OverallStats(BaseModel):
    """
    Schema for overall calculated statistics across all entries.
    """

    total_distance: float
    total_liters: float
    total_cost: float
    entry_count: int
    average_km_per_liter: float
    average_cost_per_liter: float
    best_month_efficiency: float
    best_year_efficiency: float


# --- 5. Time Period Stats Model (For Monthly/Yearly Aggregation) ---
class TimePeriodStats(BaseModel):
    """
    Schema for aggregated statistics over a specific time period
    (e.g., month or year).
    """

    period_label: str  # Example: "2024-07" or "2023"
    total_liters: float
    total_cost: float
    total_distance: float
    count: int  # Number of entries in this period
    average_km_per_liter: float
    average_cost_per_liter: float


# --- 6. Detailed Stats Response Model ---
class DetailedStats(BaseModel):
    """
    Comprehensive response model for the GET /stats/ endpoint.
    Combines overall, monthly, yearly, and optional custom range aggregations.
    """

    overall_stats: OverallStats
    monthly_stats: List[TimePeriodStats]
    yearly_stats: List[TimePeriodStats]
    custom_range_stats: Optional[List[TimePeriodStats]] = None


# --- 7. List Response Model ---
class EntryList(BaseModel):
    """
    Full response schema for the GET /entries endpoint.
    Contains the list of individual entries and the overall statistics.
    """

    entries: List[FuelEntryDB]
    overall_stats: OverallStats
