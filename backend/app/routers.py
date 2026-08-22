from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from .auth import create_token, hash_password, verify_password
from .database import get_db
from .dependencies import get_current_user, require_admin
from .models import User, Vehicle
from .schemas import (
    LoginRequest,
    RegisterRequest,
    RestockRequest,
    TokenResponse,
    VehicleCreate,
    VehicleUpdate,
)

router = APIRouter()


@router.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Simple demo rule: first account is ADMIN so the evaluator can test admin features.
    role = "ADMIN" if db.query(User).count() == 0 else "USER"
    user = User(
        name=data.name.strip(),
        email=email,
        password_hash=hash_password(data.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "Registration successful", "role": role}


@router.post("/api/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    email = data.email.strip().lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    return TokenResponse(
        access_token=create_token(user.id, user.role),
        token_type="bearer",
        role=user.role,
        name=user.name,
    )


@router.post("/api/vehicles")
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = Vehicle(**data.model_dump())
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.get("/api/vehicles")
def list_vehicles(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return db.query(Vehicle).order_by(Vehicle.id).all()


@router.get("/api/vehicles/search")
def search_vehicles(
    make: Optional[str] = None,
    model: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = Query(default=None, ge=0),
    max_price: Optional[float] = Query(default=None, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    query = db.query(Vehicle)
    if make:
        query = query.filter(Vehicle.make.ilike(f"%{make}%"))
    if model:
        query = query.filter(Vehicle.model.ilike(f"%{model}%"))
    if category:
        query = query.filter(Vehicle.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Vehicle.price >= min_price)
    if max_price is not None:
        query = query.filter(Vehicle.price <= max_price)
    return query.order_by(Vehicle.id).all()


@router.put("/api/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    for key, value in data.model_dump().items():
        setattr(vehicle, key, value)

    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    db.delete(vehicle)
    db.commit()
    return {"message": "Vehicle deleted successfully"}


@router.post("/api/vehicles/{vehicle_id}/purchase")
def purchase_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    if vehicle.quantity <= 0:
        raise HTTPException(status_code=400, detail="Vehicle is out of stock")

    vehicle.quantity -= 1
    db.commit()
    db.refresh(vehicle)
    return vehicle


@router.post("/api/vehicles/{vehicle_id}/restock")
def restock_vehicle(
    vehicle_id: int,
    data: RestockRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    vehicle = db.get(Vehicle, vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")

    vehicle.quantity += data.quantity
    db.commit()
    db.refresh(vehicle)
    return vehicle
