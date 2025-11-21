# tests/test_models.py
import pytest
from pydantic import ValidationError
from app.models import FuelEntryBase, FuelEntryDB

# --- Shared Test Data ---
VALID_DATA = {
    "date": "2024-10-25",
    "liters": 50.5,
    "price_per_liter": 1.55,
    "distance": 450.0,
    "notes": "Highway driving",
}

# --- Tests for FuelEntryBase (Validation) ---

@pytest.mark.parametrize("field, value, expected_error", [
    ("date", "25/10/2024", "Date must be in YYYY-MM-DD format."),
    ("liters", "not a float", None),
])
def test_fuelentry_base_validation_fail(field, value, expected_error):
    """Tests that invalid fields raise ValidationError with correct messages."""
    invalid_data = VALID_DATA.copy()
    invalid_data[field] = value

    with pytest.raises(ValidationError) as exc_info:
        FuelEntryBase(**invalid_data)

    if expected_error:
        assert expected_error in str(exc_info.value)

def test_fuelentry_base_creation_success():
    """Valid FuelEntryBase creation works and preserves fields."""
    entry = FuelEntryBase(**VALID_DATA)
    assert entry.liters == 50.5
    assert entry.date == "2024-10-25"
    assert entry.notes == "Highway driving"

# --- Tests for FuelEntryDB (Calculated Fields & Config) ---

@pytest.mark.parametrize("db_data, expected_cost, expected_kmpl", [
    (
        {**VALID_DATA, "id": 1, "total_cost": 78.275, "km_per_liter": 8.910891},
        78.275,
        8.910891,
    ),
    (
        {
            "id": 5,
            "date": "2023-01-01",
            "liters": 25.0,
            "price_per_liter": 1.0,
            "distance": 250.0,
            "notes": None,
            "total_cost": 25.0,
            "km_per_liter": 10.0,
        },
        25.0,
        10.0,
    ),
])
def test_fuelentry_db_creation_and_config(db_data, expected_cost, expected_kmpl):
    """FuelEntryDB creation validates calculated fields and from_attributes config."""
    entry = FuelEntryDB.model_validate(db_data)
    assert entry.id == db_data["id"]
    assert pytest.approx(entry.total_cost) == expected_cost
    assert pytest.approx(entry.km_per_liter) == expected_kmpl