# tests/test_models.py

import pytest
from pydantic import ValidationError
from datetime import date as dt
from app.models import FuelEntryBase, FuelEntryCreate, FuelEntryDB

# --- 1. Shared Test Data ---

VALID_DATA = {
    "date": "2024-10-25",
    "liters": 50.5,
    "price_per_liter": 1.55,
    "distance": 450.0,
    "notes": "Highway driving"
}

# --- 2. Tests for FuelEntryBase (Validation) ---

def test_fuelentry_base_creation_success():
    """Tests that a FuelEntryBase model can be created with valid data."""
    entry = FuelEntryBase(**VALID_DATA)
    assert entry.liters == 50.5
    assert entry.date == "2024-10-25"
    assert entry.notes == "Highway driving"

def test_fuelentry_base_date_validation_fail():
    """Tests that the date validation fails for incorrect formats."""
    invalid_data = VALID_DATA.copy()
    invalid_data['date'] = "25/10/2024" # Incorrect format
    
    with pytest.raises(ValidationError) as exc_info:
        FuelEntryBase(**invalid_data)
        
    assert "Date must be in YYYY-MM-DD format." in str(exc_info.value)
    
def test_fuelentry_base_liters_type_fail():
    """Tests that a non-float value for liters raises a validation error."""
    invalid_data = VALID_DATA.copy()
    invalid_data['liters'] = "not a float"
    
    with pytest.raises(ValidationError):
        FuelEntryBase(**invalid_data)

# --- 3. Tests for FuelEntryDB (Calculated Fields & Config) ---

def test_fuelentry_db_creation_with_all_fields():
    """Tests FuelEntryDB model creation, including derived fields."""
    db_data = VALID_DATA.copy()
    db_data.update({
        "id": 1,
        "total_cost": 78.275,  # 50.5 * 1.55
        "l_per_km": 0.112222 # 50.5 / 450.0
    })
    
    entry = FuelEntryDB(**db_data)
    assert entry.id == 1
    assert round(entry.total_cost, 2) == 78.28
    assert round(entry.l_per_km, 6) == 0.112222

def test_fuelentry_db_from_attributes_config():
    """
    Tests that the model can be instantiated from a dictionary 
    with different attribute names (simulating a database row).
    This confirms the model_config = ConfigDict(from_attributes=True) is working.
    """
    # Simulate a database row object (which uses index or keys)
    db_row_dict = {
        "id": 5,
        "date": "2023-01-01",
        "liters": 25.0,
        "price_per_liter": 1.0,
        "distance": 250.0,
        "notes": None,
        "total_cost": 25.0,
        "l_per_km": 0.1
    }
    
    # We use model_validate here, which implicitly uses from_attributes if needed.
    entry = FuelEntryDB.model_validate(db_row_dict)
    
    assert entry.id == 5
    assert entry.liters == 25.0