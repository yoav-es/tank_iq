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
    assert entry.date == "2024-10-25" # Date is stored as a string
    assert entry.notes == "Highway driving"

def test_fuelentry_base_date_validation_fail():
    """Tests that the date validation fails for incorrect formats (using the custom validator)."""
    invalid_data = VALID_DATA.copy()
    invalid_data['date'] = "25/10/2024" # Incorrect format
    
    with pytest.raises(ValidationError) as exc_info:
        FuelEntryBase(**invalid_data)
        
    # Check for the specific error message from the custom validator
    assert "Date must be in YYYY-MM-DD format." in str(exc_info.value)
    
def test_fuelentry_base_liters_type_fail():
    """Tests that a non-float value for liters raises a validation error (Pydantic core validation)."""
    invalid_data = VALID_DATA.copy()
    invalid_data['liters'] = "not a float"
    
    with pytest.raises(ValidationError):
        FuelEntryBase(**invalid_data)

# --- 3. Tests for FuelEntryDB (Calculated Fields & Config) ---

def test_fuelentry_db_creation_with_all_fields():
    """Tests FuelEntryDB model creation, ensuring calculated fields are present and correct."""
    db_data = VALID_DATA.copy()
    db_data.update({
        "id": 1,
        "total_cost": 78.275,  # 50.5 * 1.55
        # FIX: km_per_liter (450.0 km / 50.5 L ≈ 8.910891)
        "km_per_liter": 8.910891
    })
    
    entry = FuelEntryDB(**db_data)
    assert entry.id == 1
    assert pytest.approx(entry.total_cost) == 78.275
    assert pytest.approx(entry.km_per_liter) == 8.910891

def test_fuelentry_db_from_attributes_config():
    """
    Tests that the model can be instantiated from attributes (e.g., from ORM/DB row), 
    verifying model_config = ConfigDict(from_attributes=True) is working.
    """
    # Simulate a database row object
    db_row_dict = {
        "id": 5,
        "date": "2023-01-01",
        "liters": 25.0,
        "price_per_liter": 1.0,
        "distance": 250.0,
        "notes": None,
        "total_cost": 25.0,
        # FIX: km_per_liter (250.0 km / 25.0 L = 10.0)
        "km_per_liter": 10.0
    }
    
    entry = FuelEntryDB.model_validate(db_row_dict)
    
    assert entry.id == 5
    assert entry.liters == 25.0
    assert entry.km_per_liter == 10.0