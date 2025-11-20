# app/api.py
import logging
from typing import Optional, List

from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import StreamingResponse

from app.models import (
    FuelEntryCreate,
    FuelEntryDB,
    EntryList,
    DetailedStats,
    OverallStats,
    TimePeriodStats,
)
from app import database
from app.utils import get_overall_stats, convert_entries_to_csv

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/entries/", response_model=FuelEntryDB,
             status_code=status.HTTP_201_CREATED)
def create_fuel_entry(entry: FuelEntryCreate) -> FuelEntryDB:
    """Create a new fuel entry in the database."""
    db_entry = database.insert_entry(entry)
    if not db_entry:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert entry into database.",
        )
    return db_entry


@router.get("/entries/", response_model=EntryList)
def list_entries_and_stats() -> EntryList:
    """Retrieve all fuel entries and overall statistics."""
    processed_entries = database.get_all_entries_processed()
    raw_entries = database.get_all_entries_raw()
    overall_stats_data = get_overall_stats(raw_entries)

    return EntryList(
        entries=processed_entries,
        overall_stats=OverallStats(**overall_stats_data.model_dump()),
    )


@router.get("/entries/export/", tags=["Export"])
def export_entries_csv(
    start_date: Optional[str] = Query(
        None, description="Start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="End date (YYYY-MM-DD)"
    ),
) -> StreamingResponse:
    """Export fuel entries as a CSV file, optionally filtered by date range."""
    raw_entries = database.get_entries_raw(
        start_date=start_date, end_date=end_date
    )
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
def get_detailed_stats(
    start_date: Optional[str] = Query(
        None, description="Custom range start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = Query(
        None, description="Custom range end date (YYYY-MM-DD)"
    ),
) -> DetailedStats:
    """
    Retrieve overall, monthly, yearly, and optional custom range statistics.
    """
    raw_entries = database.get_all_entries_raw()
    overall_stats_model = get_overall_stats(raw_entries)

    monthly_stats = database.get_monthly_stats()
    yearly_stats = database.get_yearly_stats()

    custom_range_stats: Optional[List[TimePeriodStats]] = None
    if start_date and end_date:
        custom_range_stats = [
            database.get_custom_range_stats(start_date, end_date)
        ]

    return DetailedStats(
        overall_stats=overall_stats_model,
        monthly_stats=monthly_stats,
        yearly_stats=yearly_stats,
        custom_range_stats=custom_range_stats,
    )