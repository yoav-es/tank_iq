import logging 
from typing import Optional 
from fastapi import APIRouter, HTTPException, status, Query 
from fastapi.responses import StreamingResponse
from app.models import (
    FuelEntryCreate, FuelEntryUpdate, FuelEntryDB, EntryList, 
    DetailedStats, OverallStats 
)
from app import database # Uses the package structure
from app.utils import get_overall_stats, convert_entries_to_csv
from app.database import get_monthly_stats, get_yearly_stats 

# --- 1. LOGGING SETUP ---
logger = logging.getLogger(__name__)
# ------------------------

# --- 2. ROUTER DEFINITION (This must be here) ---
router = APIRouter()

# --- Endpoint 1: Create a new fuel entry (POST) ---
@router.post("/entries/", response_model=FuelEntryDB, status_code=status.HTTP_201_CREATED)
def create_fuel_entry(entry: FuelEntryCreate):
    """
    Creates a new fuel entry in the database.
    """
    logger.info(f"Received POST request to create entry: {entry.model_dump_json()}")
    
    db_entry = database.insert_entry(entry)
    
    if not db_entry:
        logger.error("Failed to create entry. Database insertion returned None.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert entry into database."
        )
    
    logger.info(f"Successfully created new entry with ID: {db_entry.id}")
    return db_entry

# --- Endpoint 2: Retrieve a single fuel entry by ID (GET) ---
@router.get("/entries/{entry_id}", response_model=FuelEntryDB)
def read_fuel_entry(entry_id: int):
    """
    Retrieves a single fuel entry by its ID.
    """
    logger.info(f"Received GET request for entry ID: {entry_id}")
    
    db_entry = database.read_entry(entry_id)
    
    if db_entry is None:
        logger.warning(f"Entry ID {entry_id} not found for retrieval.")
        raise HTTPException(status_code=404, detail="Entry not found")
    
    logger.info(f"Successfully retrieved entry ID: {entry_id}")
    return db_entry

# --- Endpoint 3: List all fuel entries and overall stats (GET) ---
@router.get("/entries/", response_model=EntryList)
def list_entries_and_stats():
    """
    Retrieves all fuel entries and calculates overall statistics.
    """
    logger.info("Received GET request for all entries and statistics.")

    processed_entries = database.get_all_entries_processed() 
    raw_entries = database.get_all_entries_raw() 

    overall_stats_data = get_overall_stats(raw_entries)
    
    logger.info(f"Successfully retrieved {len(processed_entries)} entries and calculated stats.")
    
    return {
        "entries": processed_entries,
        "overall_stats": OverallStats(**overall_stats_data.model_dump()) 
    }

# --- Endpoint 4: Export all entries as CSV (GET) ---
@router.get("/entries/export/", tags=["Export"])
def export_entries_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) for filtering entries."),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) for filtering entries.")
):
    """
    Retrieves fuel entries, optionally filtered by date range, and returns them 
    as a CSV file download.
    """
    logger.info(f"Received GET request for CSV data export. Filter: start={start_date}, end={end_date}.")
    
    raw_entries = database.get_entries_raw(start_date=start_date, end_date=end_date)
    csv_content = convert_entries_to_csv(raw_entries)
    
    def iter_content():
        yield csv_content

    filename = "fuel_log_export"
    if start_date or end_date:
        start = start_date.replace('-', '') if start_date else "start"
        end = end_date.replace('-', '') if end_date else "end"
        filename = f"fuel_log_{start}_to_{end}"

    return StreamingResponse(
        iter_content(),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.csv",
        }
    )

# --- Endpoint 5: Retrieve Detailed Statistical Insights (GET) ---
@router.get("/stats/", response_model=DetailedStats, tags=["Statistics"])
def get_detailed_stats():
    """
    Retrieves comprehensive statistics: overall totals, and data aggregated by month and year.
    """
    logger.info("Received GET request for detailed statistical insights.")
    
    # 1. Fetch raw data for overall stats calculation
    raw_entries = database.get_all_entries_raw()
    overall_stats_model = get_overall_stats(raw_entries)
    
    # 2. Fetch monthly and yearly aggregations from the database
    monthly_stats = get_monthly_stats()
    yearly_stats = get_yearly_stats()
    
    logger.info(f"Successfully calculated overall, {len(monthly_stats)} monthly, and {len(yearly_stats)} yearly stats.")
    
    # 3. Assemble and return the DetailedStats model
    return DetailedStats(
        overall_stats=overall_stats_model,
        monthly_stats=monthly_stats,
        yearly_stats=yearly_stats
    )


# --- Endpoint 6: Update a fuel entry (PUT) ---
@router.put("/entries/{entry_id}", response_model=FuelEntryDB)
def update_fuel_entry(entry_id: int, entry: FuelEntryUpdate):
    """
    Updates an existing fuel entry by ID.
    """
    logger.info(f"Received PUT request to update entry ID {entry_id}: {entry.model_dump_json()}")
    
    db_entry = database.update_entry(entry_id, entry)
    
    if db_entry is None:
        logger.warning(f"Failed to update entry ID {entry_id}. ID not found or database error.")
        raise HTTPException(status_code=404, detail="Entry not found or failed to update")
    
    logger.info(f"Successfully updated entry ID: {entry_id}")
    return db_entry

# --- Endpoint 7: Delete a fuel entry (DELETE) ---
@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_entry(entry_id: int):
    """
    Deletes a fuel entry by ID.
    """
    logger.info(f"Received DELETE request for entry ID: {entry_id}")
    
    success = database.delete_entry(entry_id)
    
    if not success:
        logger.warning(f"Failed to delete entry ID {entry_id}. ID not found.")
        raise HTTPException(status_code=404, detail="Entry not found")
    
    logger.info(f"Successfully deleted entry ID: {entry_id}")
    return