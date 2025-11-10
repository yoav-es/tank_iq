from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List 
from datetime import date

# --- 1. Base Model (Shared Fields) ---
class FuelEntryBase(BaseModel):
    """Base model containing fields common to all entries."""
    date: str
    liters: float
    price_per_liter: float
    distance: float
    notes: Optional[str] = None
    
    # Validation to ensure the date is in the correct format
    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        try:
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

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

    model_config = ConfigDict(
        from_attributes=True
    )

# --- 4. Overall Stats Model (FIXED) ---
class OverallStats(BaseModel):
    """
    Schema for overall calculated statistics across all entries.
    """
    total_distance: float
    total_liters: float
    total_cost: float
    entry_count: int
    average_km_per_liter: float 
    average_cost_per_liter: float # <--- This field resolves the error
# --- 5. Time Period Stats Model (For Monthly/Yearly Aggregation) ---

class TimePeriodStats(BaseModel):
    """
    Schema for aggregated statistics over a specific time period (e.g., month or year).
    """
    period_label: str # e.g., "2024-07" or "2023"
    total_liters: float
    total_cost: float
    total_distance: float
    count: int # Number of fills in this period
    average_km_per_liter: float
    average_cost_per_liter: float 

# --- 6. Detailed Stats Response Model ---

class DetailedStats(BaseModel):
    """
    The comprehensive response model for the GET /stats/ endpoint, 
    combining overall, monthly, and yearly aggregations.
    """
    overall_stats: OverallStats
    monthly_stats: List[TimePeriodStats]
    yearly_stats: List[TimePeriodStats]

# --- 7. List Response Model ---
class EntryList(BaseModel):
    """
    The full response schema for the GET /entries endpoint.
    Contains the list of individual entries and the overall statistics.
    """
    entries: List[FuelEntryDB]
    overall_stats: OverallStats