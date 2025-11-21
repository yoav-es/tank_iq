# app/database.py
import sqlite3
import logging
from typing import Optional, Generator, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path

from .models import FuelEntryCreate, FuelEntryDB, FuelEntryUpdate, TimePeriodStats
from .utils import calculate_entry_stats

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_PATH = BASE_DIR / "data" / "fuel_log.db"


def create_db_connection(db_path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Create a SQLite database connection."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    # Warn if the database file does not exist yet
    if not db_path.exists():
        logger.warning(f"Database file {db_path} not found. It will be created.")


    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db(db_path: Path = DATABASE_PATH) -> Generator[sqlite3.Connection, None, None]:
    """Context manager for database connections."""
    conn = create_db_connection(db_path)
    try:
        yield conn
    finally:
        conn.close()


def init_db(db_path: Path = DATABASE_PATH) -> None:
    """Initialize the database schema."""
    with get_db(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fuel_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                liters REAL NOT NULL,
                price_per_liter REAL NOT NULL,
                distance REAL NOT NULL,
                notes TEXT
            )
            """
        )
        conn.commit()
        logger.info("Database initialized successfully.")


def _row_to_fuel_entry_db(row: sqlite3.Row) -> FuelEntryDB:
    """Convert a SQLite row to FuelEntryDB."""
    entry_dict = dict(row)
    stats = calculate_entry_stats(
        entry_dict["liters"], entry_dict["price_per_liter"], entry_dict["distance"]
    )
    full_data = {**entry_dict, **stats}
    return FuelEntryDB.model_validate(full_data)


def _row_to_timeperiod(row: sqlite3.Row) -> TimePeriodStats:
    """Convert a SQLite row to TimePeriodStats."""
    total_liters = row["total_liters"]
    total_distance = row["total_distance"]
    total_cost = row["total_cost"]
    avg_km_per_liter = total_distance / total_liters if total_liters else 0.0
    avg_cost_per_liter = total_cost / total_liters if total_liters else 0.0
    return TimePeriodStats(
        period_label=row["period"],
        total_liters=round(total_liters, 2),
        total_cost=round(total_cost, 2),
        total_distance=round(total_distance, 2),
        count=row["count"],
        average_km_per_liter=round(avg_km_per_liter, 2),
        average_cost_per_liter=round(avg_cost_per_liter, 2),
    )


def insert_entry(entry: FuelEntryCreate) -> Optional[FuelEntryDB]:
    """Insert a new fuel entry."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO fuel_entries (date, liters, price_per_liter, distance, notes)
            VALUES (?, ?, ?, ?, ?)
            """,
            (entry.date, entry.liters, entry.price_per_liter, entry.distance, entry.notes),
        )
        conn.commit()
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (new_id,)).fetchone()
        return _row_to_fuel_entry_db(row) if row else None


def read_entry(entry_id: int) -> Optional[FuelEntryDB]:
    """Retrieve a single entry by ID."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (entry_id,)).fetchone()
        return _row_to_fuel_entry_db(row) if row else None


def update_entry(entry_id: int, entry: FuelEntryUpdate) -> Optional[FuelEntryDB]:
    """Update an existing entry by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE fuel_entries
            SET date = ?, liters = ?, price_per_liter = ?, distance = ?, notes = ?
            WHERE id = ?
            """,
            (entry.date, entry.liters, entry.price_per_liter, entry.distance, entry.notes, entry_id),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return None
        row = conn.execute("SELECT * FROM fuel_entries WHERE id = ?", (entry_id,)).fetchone()
        return _row_to_fuel_entry_db(row) if row else None


def delete_entry(entry_id: int) -> bool:
    """Delete an entry by ID."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM fuel_entries WHERE id = ?", (entry_id,))
        conn.commit()
        return cursor.rowcount > 0


def get_entries_raw(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve entries, optionally filtered by date range, as raw dicts."""
    with get_db() as conn:
        query = "SELECT * FROM fuel_entries"
        params: List[Any] = []
        if start_date and end_date:
            query += " WHERE date BETWEEN ? AND ?"
            params = [start_date, end_date]
        elif start_date:
            query += " WHERE date >= ?"
            params = [start_date]
        elif end_date:
            query += " WHERE date <= ?"
            params = [end_date]
        query += " ORDER BY date DESC"
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def get_all_entries_raw() -> List[Dict[str, Any]]:
    """Retrieve all entries as raw dicts."""
    return get_entries_raw()


def get_all_entries_processed() -> List[FuelEntryDB]:
    """Retrieve all entries as FuelEntryDB objects."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM fuel_entries ORDER BY date DESC").fetchall()
        return [_row_to_fuel_entry_db(row) for row in rows]


def get_monthly_stats() -> List[TimePeriodStats]:
    """Aggregate statistics by month."""
    with get_db() as conn:
        query = """
            SELECT strftime('%Y-%m', date) as period,
                   SUM(liters) as total_liters,
                   SUM(distance) as total_distance,
                   SUM(liters * price_per_liter) as total_cost,
                   COUNT(id) as count
            FROM fuel_entries
            GROUP BY period
            ORDER BY period DESC
        """
        rows = conn.execute(query).fetchall()
        return [_row_to_timeperiod(row) for row in rows]


def get_yearly_stats() -> List[TimePeriodStats]:
    """Aggregate statistics by year."""
    with get_db() as conn:
        query = """
            SELECT strftime('%Y', date) as period,
                   SUM(liters) as total_liters,
                   SUM(distance) as total_distance,
                   SUM(liters * price_per_liter) as total_cost,
                   COUNT(id) as count
            FROM fuel_entries
            GROUP BY period
            ORDER BY period DESC
        """
        rows = conn.execute(query).fetchall()
        return [_row_to_timeperiod(row) for row in rows]


def get_custom_range_stats(start_date: str, end_date: str) -> TimePeriodStats:
    """Aggregate statistics for a custom date range."""
    with get_db() as conn:
        query = """
            SELECT SUM(liters) as total_liters,
                   SUM(distance) as total_distance,
                   SUM(liters * price_per_liter) as total_cost,
                   COUNT(id) as count
            FROM fuel_entries
            WHERE date BETWEEN ? AND ?
        """
        row = conn.execute(query, (start_date, end_date)).fetchone()
        if not row or row["count"] == 0:
            return TimePeriodStats(
                period_label=f"{start_date}_to_{end_date}",
                total_liters=0.0,
                total_cost=0.0,
                total_distance=0.0,
                count=0,
                average_km_per_liter=0.0,
                average_cost_per_liter=0.0,
            )
        total_liters = row["total_liters"]
        total_distance = row["total_distance"]
        total_cost = row["total_cost"]
        avg_km_per_liter = total_distance / total_liters if total_liters else 0.0
        avg_cost_per_liter = total_cost / total_liters if total_liters else 0.0
        return TimePeriodStats(
            period_label=f"{start_date}_to_{end_date}",
            total_liters=round(total_liters, 2),
            total_cost=round(total_cost, 2),
            total_distance=round(total_distance, 2),
            count=row["count"],
            average_km_per_liter=round(avg_km_per_liter, 2),
            average_cost_per_liter=round(avg_cost_per_liter, 2),
        )