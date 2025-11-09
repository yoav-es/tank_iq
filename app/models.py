from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List # List is now imported
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

# --- 2. Input/Create Model (For POST/PUT Requests) ---
class FuelEntryCreate(FuelEntryBase):
    """Schema for receiving new data from a POST/PUT request."""
    pass

class FuelEntryUpdate(FuelEntryBase):
    """Schema for updating an existing entry."""
    pass

# --- 3. Database/Output Model (For GET Responses) ---
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

# --- 4. Overall Stats Model ---
class OverallStats(BaseModel):
    """
    Schema for overall calculated statistics across all entries.
    """
    total_distance: float
    total_liters: float
    total_cost: float
    entry_count: int
    # RENAMED: from average_l_per_100km to average_km_per_liter
    average_km_per_liter: float 

# --- 5. List Response Model ---
class EntryList(BaseModel):
    """
    The full response schema for the GET /entries endpoint.
    Contains the list of individual entries and the overall statistics.
    """
    entries: List[FuelEntryDB]
    overall_stats: OverallStats