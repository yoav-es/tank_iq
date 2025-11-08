# app/models.py

from pydantic import BaseModel, field_validator, ConfigDict # <-- UPDATED IMPORT: ConfigDict
from typing import Optional
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

# --- 3. Database/Output Model (For GET Responses) ---
class FuelEntryDB(FuelEntryBase):
    """
    Schema for data retrieved from the database and sent as a response.
    Includes the database ID and calculated properties.
    """
    id: int
    total_cost: float
    l_per_km: float

    # --- REPLACED: Use model_config (ConfigDict) to eliminate Pydantic V2 warning ---
    model_config = ConfigDict(
        from_attributes=True # This replaces the old Config.from_attributes = True
    )