"""
Backfill module: fetches full historical yield curve data from FRED
and upserts into yield_curve_rates.

Each FRED series is a CSV of (DATE, value) going back decades.
Missing values (reported as ".") are stored as NULL.

Run locally:
    make backfill
    docker compose run --rm pipeline python -m src.backfill

On AWS:
    Run as a one-off ECS task (same image, different command).
"""

import logging
import sys
import time
from datetime import date
from io import StringIO

import pandas as pd
import requests

from src.loader import RateRecord, get_fred_series, upsert_rates

log = logging.getLogger(__name__)

FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"

FIRST_YIELD_DATE = date(2010, 1, 1)

# Courtesy delay between FRED requests (they're generous but let's be polite)
_REQUEST_DELAY_SECONDS = 0.5


def fetch_series(series_id: str, tenor: str) -> list[RateRecord]:
    """Download the full history for one FRED series, filtered to FIRST_YIELD_DATE onward."""
    log.info("Fetching %s (%s)...", series_id, tenor)
    url = f"{FRED_CSV_URL}?id={series_id}&cosd={FIRST_YIELD_DATE.isoformat()}"
    df = pd.read_csv(StringIO(requests.get(url, timeout=15).text), parse_dates=['observation_date'], na_values=".")

    records = [
        RateRecord(date=row.observation_date, tenor=tenor, rate=None if pd.isna(getattr(row, series_id)) else float(getattr(row, series_id)))
        for row in df.itertuples(index=False)
    ]
    log.info("  → %d rows (incl. nulls)", len(records))
    return records


def fetch_today() -> list[RateRecord]:
    """Fetch all tenors for today only — used by the daily pipeline job."""
    today = date.today()
    date_str = today.isoformat()
    fred_series = get_fred_series()
    all_records: list[RateRecord] = []
    for series_id, tenor in fred_series.items():
        url = f"{FRED_CSV_URL}?id={series_id}&cosd={FIRST_YIELD_DATE.isoformat()}&coed={date_str}"
        df = pd.read_csv(StringIO(requests.get(url, timeout=15).text), parse_dates=["observation_date"], na_values=".")
        all_records.extend(
            RateRecord(date=row.observation_date, tenor=tenor, rate=None if pd.isna(getattr(row, series_id)) else float(getattr(row, series_id)))
            for row in df.itertuples(index=False)
        )
    return all_records


def run(dry_run: bool = False) -> None:
    fred_series = get_fred_series()
    log.info("Loaded %d series from tenors table.", len(fred_series))
    all_records: list[RateRecord] = []

    for series_id, tenor in fred_series.items():
        records = fetch_series(series_id, tenor)
        all_records.extend(records)
        time.sleep(_REQUEST_DELAY_SECONDS)

    log.info("Total records fetched: %d", len(all_records))

    if dry_run:
        log.info("Dry run — skipping DB write.")
        return

    inserted = upsert_rates(all_records)
    log.info("Inserted %d new rows into yield_curve_rates.", inserted)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        stream=sys.stdout,
    )
    dry_run = "--dry-run" in sys.argv
    if dry_run:
        log.info("DRY RUN mode — no DB writes.")
    run(dry_run=dry_run)
