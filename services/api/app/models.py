from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    term: Mapped[str] = mapped_column(String(10), ForeignKey("tenors.code"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="orders")
    tenor: Mapped["Tenor"] = relationship(foreign_keys=[term], primaryjoin="Order.term == Tenor.code")


class Tenor(Base):
    __tablename__ = "tenors"

    id: Mapped[int] = mapped_column(primary_key=True)
    fred_series_id: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(10), nullable=False, unique=True)
    maturity_years: Mapped[Decimal] = mapped_column(Numeric(7, 4), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)

    rates: Mapped[list["YieldCurveRate"]] = relationship(back_populates="tenor")


class YieldCurveRate(Base):
    __tablename__ = "yield_curve_rates"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    tenor_id: Mapped[int] = mapped_column(ForeignKey("tenors.id"), nullable=False)
    rate: Mapped[Decimal | None] = mapped_column(Numeric(7, 3), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    tenor: Mapped["Tenor"] = relationship(back_populates="rates")

    __table_args__ = (
        UniqueConstraint("date", "tenor_id", name="uq_yield_curve_date_tenor"),
        Index("idx_yield_curve_rates_date", "date"),
    )
