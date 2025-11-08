# tests/test_models.py

import pytest
from app.models import FuelEntry 
from datetime import date

# Define a fixture for clean code
@pytest.fixture
def sample_entry():
    """Returns a standard FuelEntry instance for testing calculated properties."""
    return FuelEntry(
        date=str(date.today()),
        liters=50.0,
        price_per_liter=1.50,
        distance=600.0,
        notes="Standard test fill"
    )

def test_entry_creation(sample_entry):
    """Verifies basic instantiation and attribute assignment."""
    assert sample_entry.liters == 50.0

def test_calculated_total_cost(sample_entry):
    """Verifies the total_cost calculation (50.0 * 1.50 = 75.0)."""
    assert sample_entry.total_cost == 75.0

def test_calculated_l_per_km():
    """Verifies the L/km calculation (30 / 400 = 0.075)."""
    entry = FuelEntry(date="2025-01-01", liters=30.0, price_per_liter=2.0, distance=400.0)
    assert entry.l_per_km == 0.075

def test_l_per_km_zero_distance():
    """Verifies L/km calculation handles zero distance."""
    entry = FuelEntry(date="2025-01-01", liters=20.0, price_per_liter=1.0, distance=0.0)
    assert entry.l_per_km == 0.0