import logging
from dataclasses import dataclass
from datetime import date

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from src.settings import settings

log = logging.getLogger(__name__)

_engine = create_engine(settings.database_url, pool_pre_ping=True)
_Session = sessionmaker(bind=_engine)


@dataclass
class RateRecord:
    date: date
    tenor: str   # tenor code e.g. '10Y'
    rate: float | None


def get_fred_series() -> dict[str, str]:
    """Return {fred_series_id: tenor_code} from the tenors reference table."""
    with _Session() as session:
        rows = session.execute(
            text("SELECT fred_series_id, code FROM tenors ORDER BY sort_order")
        ).all()
    return {fred_series_id: code for fred_series_id, code in rows}


def upsert_rates(records: list[RateRecord]) -> int:
    """
    Upsert records into yield_curve_rates via tenor code lookup.
    Skips any tenor codes not present in the tenors reference table.
    Returns the number of newly inserted rows.
    """
    if not records:
        return 0

    with _Session() as session:
        tenor_map: dict[str, int] = dict(
            session.execute(text("SELECT code, id FROM tenors")).all()
        )
        unknown = {r.tenor for r in records} - tenor_map.keys()
        if unknown:
            log.warning("Skipping unknown tenor codes: %s", unknown)

        rows = [
            {"date": r.date, "tenor_id": tenor_map[r.tenor], "rate": r.rate}
            for r in records
            if r.tenor in tenor_map
        ]

        result = session.execute(
            text("""
                INSERT INTO yield_curve_rates (date, tenor_id, rate)
                VALUES (:date, :tenor_id, :rate)
                ON CONFLICT (date, tenor_id) DO NOTHING
            """),
            rows,
        )
        session.commit()

    inserted = result.rowcount
    log.info("Upserted %d records (%d new)", len(rows), inserted)
    return inserted
