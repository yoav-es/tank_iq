# app/api.py
"""
TankIQ API Module

This module defines the FastAPI routes for CRUD operations,
statistics retrieval, and CSV export of fuel entries.
It handles request validation, error responses, and logging.
"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from app.models import (
    FuelEntryCreate,
    FuelEntryUpdate,
    FuelEntryDB,
    EntryList,
    DetailedStats,
    OverallStats,  # Used indirectly inside EntryList and DetailedStats response models,
)
from app import database
from app.utils import get_overall_stats, convert_entries_to_csv
from app.database import get_monthly_stats, get_yearly_stats

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/entries/", response_model=FuelEntryDB, status_code=status.HTTP_201_CREATED)
def create_fuel_entry(entry: FuelEntryCreate) -> FuelEntryDB:
    """
    Create a new fuel entry in the database.

    Args:
        entry (FuelEntryCreate): Data for the new fuel entry.

    Returns:
        FuelEntryDB: The created fuel entry record.
    """
    logger.info("Received POST request to create entry.")

    db_entry = database.insert_entry(entry)
    if not db_entry:
        logger.error("Failed to create entry. Database insertion returned None.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert entry into database.",
        )

    logger.info("Successfully created new entry with ID: %s", db_entry.id)
    return db_entry


@router.get("/entries/{entry_id}", response_model=FuelEntryDB)
def read_fuel_entry(entry_id: int) -> FuelEntryDB:
    """
    Retrieve a single fuel entry by ID.

    Args:
        entry_id (int): The ID of the fuel entry.

    Returns:
        FuelEntryDB: The requested fuel entry record.
    """
    logger.info("Received GET request for entry ID: %s", entry_id)

    db_entry = database.read_entry(entry_id)
    if db_entry is None:
        logger.warning("Entry ID %s not found for retrieval.", entry_id)
        raise HTTPException(status_code=404, detail="Entry not found")

    logger.info("Successfully retrieved entry ID: %s", entry_id)
    return db_entry


@router.get("/entries/", response_model=EntryList)
def list_entries_and_stats() -> EntryList:
    """
    Retrieve all fuel entries and overall statistics.

    Returns:
        EntryList: List of processed entries and overall statistics.
    """
    logger.info("Received GET request for all entries and statistics.")

    processed_entries = database.get_all_entries_processed()
    raw_entries = database.get_all_entries_raw()

    monthly_stats = get_monthly_stats() or []
    yearly_stats = get_yearly_stats() or []

    overall_stats_model = get_overall_stats(
        raw_entries,
        monthly_stats=monthly_stats,
        yearly_stats=yearly_stats,
    )

    logger.info(
        "Successfully retrieved %d entries and calculated stats.",
        len(processed_entries),
    )

    return EntryList(
        entries=processed_entries,
        overall_stats=overall_stats_model,
    )


@router.get("/entries/export/", tags=["Export"])
def export_entries_csv(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
) -> StreamingResponse:
    """
    Export fuel entries as a CSV file, optionally filtered by date range.

    Args:
        start_date (Optional[str]): Start date filter in YYYY-MM-DD format.
        end_date (Optional[str]): End date filter in YYYY-MM-DD format.

    Returns:
        StreamingResponse: CSV file containing fuel entries.
    """
    logger.info(
        "Received GET request for CSV export. Filter: start=%s, end=%s",
        start_date,
        end_date,
    )

    raw_entries = database.get_entries_raw(start_date=start_date, end_date=end_date)
    csv_content = convert_entries_to_csv(raw_entries)

    def iter_content():
        yield csv_content

    filename = "fuel_log_export"
    if start_date or end_date:
        start = start_date.replace("-", "") if start_date else "start"
        end = end_date.replace("-", "") if end_date else "end"
        filename = f"fuel_log_{start}_to_{end}"

    return StreamingResponse(
        iter_content(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}.csv"},
    )


@router.get("/stats/", response_model=DetailedStats, tags=["Statistics"])
def get_detailed_stats() -> DetailedStats:
    """
    Retrieve overall, monthly, and yearly statistics.

    Returns:
        DetailedStats: Aggregated statistics including overall, monthly, and yearly data.
    """
    logger.info("Received GET request for detailed statistical insights.")

    raw_entries = database.get_all_entries_raw()
    monthly_stats = get_monthly_stats() or []
    yearly_stats = get_yearly_stats() or []

    overall_stats_model = get_overall_stats(
        raw_entries,
        monthly_stats=monthly_stats,
        yearly_stats=yearly_stats,
    )

    logger.info(
        "Successfully calculated overall, %d monthly, and %d yearly stats.",
        len(monthly_stats),
        len(yearly_stats),
    )

    return DetailedStats(
        overall_stats=overall_stats_model,
        monthly_stats=monthly_stats,
        yearly_stats=yearly_stats,
    )


@router.put("/entries/{entry_id}", response_model=FuelEntryDB)
def update_fuel_entry(entry_id: int, entry: FuelEntryUpdate) -> FuelEntryDB:
    """
    Update an existing fuel entry by ID.

    Args:
        entry_id (int): The ID of the fuel entry to update.
        entry (FuelEntryUpdate): Updated data for the fuel entry.

    Returns:
        FuelEntryDB: The updated fuel entry record.
    """
    logger.info("Received PUT request to update entry ID %s.", entry_id)

    db_entry = database.update_entry(entry_id, entry)
    if db_entry is None:
        logger.warning("Failed to update entry ID %s. Not found or database error.", entry_id)
        raise HTTPException(status_code=404, detail="Entry not found or failed to update")

    logger.info("Successfully updated entry ID: %s", entry_id)
    return db_entry


@router.delete("/entries/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fuel_entry(entry_id: int) -> None:
    """
    Delete a fuel entry by ID.

    Args:
        entry_id (int): The ID of the fuel entry to delete.

    Returns:
        None
    """
    logger.info("Received DELETE request for entry ID: %s", entry_id)

    success = database.delete_entry(entry_id)
    if not success:
        logger.warning("Failed to delete entry ID %s. Not found.", entry_id)
        raise HTTPException(status_code=404, detail="Entry not found")

    logger.info("Successfully deleted entry ID: %s", entry_id)
    return None


@router.delete("/entries/", status_code=status.HTTP_204_NO_CONTENT, tags=["Maintenance"])
def purge_all_entries() -> None:
    """
    Delete ALL fuel entries and vacuum the database.

    Returns:
        None
    """
    logger.warning("Received DELETE request to purge ALL entries.")

    success = database.delete_all_entries()
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to purge entries."
        )

    logger.info("Successfully purged all entries and vacuumed database.")
    return None
