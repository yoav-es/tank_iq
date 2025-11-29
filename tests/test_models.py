"""
TankIQ Models Tests

Unit tests for Pydantic models defined in app/models.py.
Verifies validation rules, field preservation, and required attributes.
"""

import pytest
from pydantic import ValidationError
from app.models import (
    EntryList,
    DetailedStats,
    FuelEntryBase,
    FuelEntryCreate,
    FuelEntryUpdate,
    FuelEntryDB,
    OverallStats,
    TimePeriodStats,
)

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
    """Invalid fields raise ValidationError with correct messages."""
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

# --- Tests for FuelEntryCreate / FuelEntryUpdate ---

def test_fuel_entry_create_inherits_from_base():
    """FuelEntryCreate has same fields as FuelEntryBase."""
    entry = FuelEntryCreate(**VALID_DATA)
    assert entry.date == VALID_DATA["date"]
    assert entry.distance == VALID_DATA["distance"]

def test_fuel_entry_update_requires_all_fields():
    """FuelEntryUpdate inherits FuelEntryBase and requires all fields."""
    entry = FuelEntryUpdate(**VALID_DATA)
    assert entry.liters == VALID_DATA["liters"]
    assert entry.notes == VALID_DATA["notes"]

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

def test_fuel_entry_db_includes_id_and_fields():
    """FuelEntryDB includes id, total_cost, and km_per_liter."""
    entry = FuelEntryDB(
        id=1,
        date="2024-11-01",
        liters=20.0,
        price_per_liter=2.5,
        distance=200.0,
        notes="Errand",
        total_cost=50.0,
        km_per_liter=10.0,
    )
    assert entry.id == 1
    assert entry.total_cost == 50.0
    assert entry.km_per_liter == 10.0

# --- Tests for OverallStats / TimePeriodStats ---

def test_overall_stats_model_fields():
    """OverallStats requires best_month_efficiency and best_year_efficiency."""
    stats = OverallStats(
        total_liters=100.0,
        total_cost=200.0,
        total_distance=1500.0,
        entry_count=3,
        average_km_per_liter=15.0,
        average_cost_per_liter=2.0,
        best_month_efficiency=16.5,
        best_year_efficiency=15.8,
    )
    assert stats.entry_count == 3
    assert stats.best_month_efficiency == 16.5
    assert stats.best_year_efficiency == 15.8

def test_time_period_stats_model_fields():
    """TimePeriodStats requires all aggregation fields."""
    stats = TimePeriodStats(
        period_label="2024-11",
        total_liters=50.0,
        total_cost=100.0,
        total_distance=800.0,
        count=2,
        average_km_per_liter=16.0,
        average_cost_per_liter=2.0,
    )
    assert stats.period_label == "2024-11"
    assert stats.count == 2

# --- Extra Validation Test ---

def test_invalid_date_and_negative_values_raise_validation_error():
    """Invalid date format and negative values raise ValidationError."""
    with pytest.raises(ValidationError):
        FuelEntryBase(
            date="11/01/2024",  # invalid format
            liters=10.0,
            price_per_liter=2.0,
            distance=100.0,
        )
    with pytest.raises(ValidationError):
        FuelEntryBase(
            date="2024-11-01",
            liters=-10.0,  # invalid negative liters
            price_per_liter=2.0,
            distance=100.0,
        )


def test_detailed_stats_with_and_without_custom_range():
    """DetailedStats composes overall, monthly, yearly, and optional custom range stats."""
    overall = OverallStats(
        total_distance=1000.0,
        total_liters=80.0,
        total_cost=160.0,
        entry_count=2,
        average_km_per_liter=12.5,
        average_cost_per_liter=2.0,
        best_month_efficiency=13.0,
        best_year_efficiency=12.8,
    )
    monthly = [
        TimePeriodStats(
            period_label="2024-10",
            total_liters=40.0,
            total_cost=80.0,
            total_distance=600.0,
            count=1,
            average_km_per_liter=15.0,
            average_cost_per_liter=2.0,
        )
    ]
    yearly = [
        TimePeriodStats(
            period_label="2024",
            total_liters=80.0,
            total_cost=160.0,
            total_distance=1000.0,
            count=2,
            average_km_per_liter=12.5,
            average_cost_per_liter=2.0,
        )
    ]

    # Without custom range
    ds1 = DetailedStats(
        overall_stats=overall,
        monthly_stats=monthly,
        yearly_stats=yearly,
    )
    assert ds1.custom_range_stats is None
    assert len(ds1.monthly_stats) == 1 and len(ds1.yearly_stats) == 1

    # With custom range
    custom = [
        TimePeriodStats(
            period_label="2024-11-01..2024-11-15",
            total_liters=20.0,
            total_cost=40.0,
            total_distance=250.0,
            count=1,
            average_km_per_liter=12.5,
            average_cost_per_liter=2.0,
        )
    ]
    ds2 = DetailedStats(
        overall_stats=overall,
        monthly_stats=monthly,
        yearly_stats=yearly,
        custom_range_stats=custom,
    )
    assert ds2.custom_range_stats is not None
    assert len(ds2.custom_range_stats) == 1

def test_entry_list_structure():
    """EntryList includes list of FuelEntryDB and OverallStats."""
    entry1 = FuelEntryDB(
        id=1,
        date="2024-11-05",
        liters=30.0,
        price_per_liter=2.0,
        distance=450.0,
        notes=None,
        total_cost=60.0,
        km_per_liter=15.0,
    )
    entry2 = FuelEntryDB(
        id=2,
        date="2024-11-06",
        liters=25.0,
        price_per_liter=1.9,
        distance=400.0,
        notes="Commute",
        total_cost=47.5,
        km_per_liter=16.0,
    )
    overall = OverallStats(
        total_distance=850.0,
        total_liters=55.0,
        total_cost=107.5,
        entry_count=2,
        average_km_per_liter=15.45,
        average_cost_per_liter=1.955,
        best_month_efficiency=16.0,
        best_year_efficiency=16.0,
    )
    resp = EntryList(entries=[entry1, entry2], overall_stats=overall)
    assert len(resp.entries) == 2
    assert resp.overall_stats.entry_count == 2
