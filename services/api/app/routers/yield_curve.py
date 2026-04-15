from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Tenor, YieldCurveRate
from app.schemas import AvailableDatesResponse, RateRow, YieldCurvePoint, YieldCurveSnapshot

router = APIRouter(prefix="/yield-curve", tags=["yield-curve"])


@router.get("/history", response_model=list[RateRow])
def get_history(
    start: date | None = Query(default=None),
    end: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Return a flat list of all rate records, optionally filtered by date range."""
    q = (
        select(YieldCurveRate)
        .join(YieldCurveRate.tenor)
        .options(joinedload(YieldCurveRate.tenor))
        .order_by(YieldCurveRate.date.asc(), Tenor.sort_order.asc())
    )
    if start:
        q = q.where(YieldCurveRate.date >= start)
    if end:
        q = q.where(YieldCurveRate.date <= end)

    rows = db.execute(q).scalars().all()
    return [
        RateRow(
            date=r.date,
            tenor=r.tenor.code,
            maturity_years=float(r.tenor.maturity_years),
            rate=float(r.rate) if r.rate is not None else None,
        )
        for r in rows
    ]


@router.get("/dates", response_model=AvailableDatesResponse)
def list_available_dates(
    limit: int = Query(default=30, le=500),
    db: Session = Depends(get_db),
):
    """Return the most recent dates for which yield curve data exists."""
    rows = db.execute(
        select(func.distinct(YieldCurveRate.date))
        .order_by(YieldCurveRate.date.desc())
        .limit(limit)
    ).scalars().all()
    return AvailableDatesResponse(dates=rows)


@router.get("/latest", response_model=YieldCurveSnapshot)
def get_latest(db: Session = Depends(get_db)):
    """Return the most recent yield curve snapshot."""
    latest_date = db.execute(
        select(func.max(YieldCurveRate.date))
    ).scalar_one_or_none()

    if latest_date is None:
        raise HTTPException(status_code=404, detail="No yield curve data available yet.")

    return _snapshot_for_date(latest_date, db)


@router.get("/{curve_date}", response_model=YieldCurveSnapshot)
def get_by_date(curve_date: date, db: Session = Depends(get_db)):
    """Return the yield curve for a specific date (YYYY-MM-DD)."""
    snapshot = _snapshot_for_date(curve_date, db)
    if not snapshot.rates:
        raise HTTPException(status_code=404, detail=f"No data for {curve_date}.")
    return snapshot


def _snapshot_for_date(curve_date: date, db: Session) -> YieldCurveSnapshot:
    rows = db.execute(
        select(YieldCurveRate)
        .options(joinedload(YieldCurveRate.tenor))
        .where(YieldCurveRate.date == curve_date)
        .order_by(Tenor.sort_order)
        .join(YieldCurveRate.tenor)
    ).scalars().all()

    return YieldCurveSnapshot(
        date=curve_date,
        rates=[
            YieldCurvePoint(
                tenor=r.tenor.code,
                maturity_years=float(r.tenor.maturity_years),
                rate=float(r.rate) if r.rate is not None else None,
            )
            for r in rows
        ],
    )
