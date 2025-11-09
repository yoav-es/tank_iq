# app/api.py

from fastapi import APIRouter, HTTPException, status
from app.models import FuelEntryCreate, FuelEntryUpdate, FuelEntryDB, EntryList
from app import database
from app.utils import get_overall_stats

router = APIRouter()

# --- Endpoint 1: Create a new fuel entry (POST) ---
@router.post("/entries/", response_model=FuelEntryDB, status_code=status.HTTP_201_CREATED)
def create_fuel_entry(entry: FuelEntryCreate):
    """
    Creates a new fuel entry in the database.
    Returns the created entry, including calculated fields and the database ID.
    """
    db_entry = database.insert_entry(entry)
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert entry into database."
        )
    return db_entry

# --- Endpoint 2: Retrieve a single fuel entry by ID (GET) ---
@router.get("/entries/{entry_id}", response_model=FuelEntryDB)
def read_fuel_entry(entry_id: int):
    """
    Retrieves a single fuel entry by its ID.
    """
    db_entry = database.read_entry(entry_id)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return db_entry

# --- Endpoint 3: List all fuel entries and overall stats (GET) ---
@router.get("/entries/", response_model=EntryList)
def list_entries_and_stats():
    """
    Retrieves all fuel entries and calculates overall statistics.
    Returns the list of entries (with calculated fields) and the statistics.
    """
    # CRITICAL FIX: Retrieve PROCESSED entries for the list (satisfies FuelEntryDB model)
    processed_entries = database.get_all_entries_processed() 
    
    # Retrieve RAW entries for overall stats calculation (needed for accurate sums)
    raw_entries = database.get_all_entries_raw()

    overall_stats = get_overall_stats(raw_entries)
    
    return {
        "entries": processed_entries,
        "overall_stats": overall_stats
    }


# --- Endpoint 4: Update a fuel entry (PUT) ---
@router.put("/entries/{entry_id}", response_model=FuelEntryDB)
def update_fuel_entry(entry_id: int, entry: FuelEntryUpdate):
    """
    Updates an existing fuel entry by ID.
    """
    db_entry = database.update_entry(entry_id, entry)
    if db_entry is None:
        raise HTTPException(status_code=404, detail="Entry not found or failed to update")
    return db_entry

# --- Endpoint 5: Delete a fuel entry (DELETE) ---
@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_entry(entry_id: int):
    """
    Deletes a fuel entry by ID.
    """
    success = database.delete_entry(entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    return