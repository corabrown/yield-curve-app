from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order, Tenor, User
from app.schemas import OrderCreate, OrderResponse, UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


def _get_user_or_404(user_id: int, db: Session) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail=f"No user with ID {user_id}.")
    return user


def _get_valid_tenors(db: Session) -> list[str]:
    return db.execute(select(Tenor.code).order_by(Tenor.sort_order)).scalars().all()


@router.post("", response_model=UserResponse, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    existing = db.execute(select(User).where(User.first_name == body.first_name)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail=f"A user named '{body.first_name}' already exists (ID: {existing.id}).")
    user = User(first_name=body.first_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return _get_user_or_404(user_id, db)


@router.post("/{user_id}/orders", response_model=OrderResponse, status_code=201)
def create_order(user_id: int, body: OrderCreate, db: Session = Depends(get_db)):
    _get_user_or_404(user_id, db)

    if body.amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be greater than zero.")

    valid_tenors = _get_valid_tenors(db)
    if body.term not in valid_tenors:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid term '{body.term}'. Valid options are: {', '.join(valid_tenors)}.",
        )

    order = Order(user_id=user_id, term=body.term, amount=body.amount)
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/{user_id}/orders", response_model=list[OrderResponse])
def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    _get_user_or_404(user_id, db)

    orders = db.execute(
        select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
    ).scalars().all()
    return orders
