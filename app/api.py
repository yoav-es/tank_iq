import logging # <-- NEW: Import logging
from fastapi import APIRouter, HTTPException, status
from app.models import FuelEntryCreate, FuelEntryUpdate, FuelEntryDB, EntryList
from app import database
from app.utils import get_overall_stats

# --- 1. LOGGING SETUP ---
logger = logging.getLogger(__name__)
# ------------------------

router = APIRouter()

# --- Endpoint 1: Create a new fuel entry (POST) ---
@router.post("/entries/", response_model=FuelEntryDB, status_code=status.HTTP_201_CREATED)
def create_fuel_entry(entry: FuelEntryCreate):
    """
    Creates a new fuel entry in the database.
    Returns the created entry, including calculated fields and the database ID.
    """
    # INFO Log: Incoming request
    logger.info(f"Received POST request to create entry: {entry.model_dump_json()}")
    
    db_entry = database.insert_entry(entry)
    
    if not db_entry:
        # ERROR Log: Insertion failed (DB already logs the specific sqlite error)
        logger.error("Failed to create entry. Database insertion returned None.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert entry into database."
        )
    
    # INFO Log: Successful creation
    logger.info(f"Successfully created new entry with ID: {db_entry.id}")
    return db_entry

# --- Endpoint 2: Retrieve a single fuel entry by ID (GET) ---
@router.get("/entries/{entry_id}", response_model=FuelEntryDB)
def read_fuel_entry(entry_id: int):
    """
    Retrieves a single fuel entry by its ID.
    """
    # INFO Log: Incoming request
    logger.info(f"Received GET request for entry ID: {entry_id}")
    
    db_entry = database.read_entry(entry_id)
    
    if db_entry is None:
        # WARNING Log: ID not found (DB logs the warning)
        logger.warning(f"Entry ID {entry_id} not found for retrieval.")
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # INFO Log: Successful retrieval
    logger.info(f"Successfully retrieved entry ID: {entry_id}")
    return db_entry

# --- Endpoint 3: List all fuel entries and overall stats (GET) ---
@router.get("/entries/", response_model=EntryList)
def list_entries_and_stats():
    """
    Retrieves all fuel entries and calculates overall statistics.
    Returns the list of entries (with calculated fields) and the statistics.
    """
    # INFO Log: Incoming request
    logger.info("Received GET request for all entries and statistics.")

    processed_entries = database.get_all_entries_processed() 
    raw_entries = database.get_all_entries_raw()

    overall_stats = get_overall_stats(raw_entries)
    
    # INFO Log: Successful list operation
    logger.info(f"Successfully retrieved {len(processed_entries)} entries and calculated stats.")
    
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
    # INFO Log: Incoming request
    logger.info(f"Received PUT request to update entry ID {entry_id}: {entry.model_dump_json()}")
    
    db_entry = database.update_entry(entry_id, entry)
    
    if db_entry is None:
        # WARNING Log: Failed update (DB logs warning/error)
        logger.warning(f"Failed to update entry ID {entry_id}. ID not found or database error.")
        raise HTTPException(status_code=404, detail="Entry not found or failed to update")
    
    # INFO Log: Successful update
    logger.info(f"Successfully updated entry ID: {entry_id}")
    return db_entry

# --- Endpoint 5: Delete a fuel entry (DELETE) ---
@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_entry(entry_id: int):
    """
    Deletes a fuel entry by ID.
    """
    # INFO Log: Incoming request
    logger.info(f"Received DELETE request for entry ID: {entry_id}")
    
    success = database.delete_entry(entry_id)
    
    if not success:
        # WARNING Log: Failed deletion (DB logs warning)
        logger.warning(f"Failed to delete entry ID {entry_id}. ID not found.")
        raise HTTPException(status_code=404, detail="Entry not found")
    
    # INFO Log: Successful deletion
    logger.info(f"Successfully deleted entry ID: {entry_id}")
    return