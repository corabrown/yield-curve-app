from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class YieldCurvePoint(BaseModel):
    tenor: str
    maturity_years: float
    rate: float | None

    model_config = {"from_attributes": True}


class YieldCurveSnapshot(BaseModel):
    date: date
    rates: list[YieldCurvePoint]


class AvailableDatesResponse(BaseModel):
    dates: list[date]


class RateRow(BaseModel):
    date: date
    tenor: str
    maturity_years: float
    rate: float | None

    model_config = {"from_attributes": True}


# ── Users ─────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    first_name: str


class UserResponse(BaseModel):
    id: int
    first_name: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Orders ────────────────────────────────────────────────────────────────────

class OrderCreate(BaseModel):
    term: str
    amount: Decimal


class OrderResponse(BaseModel):
    id: int
    user_id: int
    term: str
    amount: Decimal
    created_at: datetime

    model_config = {"from_attributes": True}
