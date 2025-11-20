# app/models.py
from datetime import date
from typing import Optional, List

from pydantic import BaseModel, field_validator, ConfigDict


# --- 1. Base Model (Shared Fields) ---
class FuelEntryBase(BaseModel):
    """Base model containing fields common to all entries."""

    date: str
    liters: float
    price_per_liter: float
    distance: float
    notes: Optional[str] = None

    @field_validator("date")
    @classmethod
    def validate_date_format(cls, value: str) -> str:
        """Ensure the date is in YYYY-MM-DD format."""
        try:
            date.fromisoformat(value)
            return value
        except ValueError as exc:
            raise ValueError("Date must be in YYYY-MM-DD format.") from exc


# --- 2. Input/Create/Update Models ---
class FuelEntryCreate(FuelEntryBase):
    """Schema for receiving new data from a POST request."""
    pass


class FuelEntryUpdate(FuelEntryBase):
    """Schema for updating an existing entry."""
    pass


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
    """Schema for overall calculated statistics across all entries."""

    total_distance: float
    total_liters: float
    total_cost: float
    entry_count: int
    average_km_per_liter: float
    average_cost_per_liter: float


# --- 5. Time Period Stats Model (For Monthly/Yearly Aggregation) ---
class TimePeriodStats(BaseModel):
    """
    Schema for aggregated statistics over a specific time period
    (e.g., month or year).
    """

    period_label: str  # e.g., "2024-07" or "2023"
    total_liters: float
    total_cost: float
    total_distance: float
    count: int  # Number of fills in this period
    average_km_per_liter: float
    average_cost_per_liter: float


# --- 6. Detailed Stats Response Model ---
class DetailedStats(BaseModel):
    """
    Comprehensive response model for the GET /stats/ endpoint,
    combining overall, monthly, yearly, and optional custom range aggregations.
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