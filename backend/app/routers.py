from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .database import get_db
from .models import User, Vehicle
from .schemas import (
    RegisterRequest,
    RestockRequest,
    TokenResponse,
    VehicleCreate,
    VehicleUpdate,
)
from .auth import (
    hash_password,
    verify_password,
    create_token,
)
from .dependencies import get_current_user


router = APIRouter()


# AUTHENTICATION
@router.post("/api/auth/register", status_code=201)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    email = data.email.strip().lower()

    existing_user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # First user becomes ADMIN
    user_count = db.query(User).count()

    role = "ADMIN" if user_count == 0 else "USER"

    user = User(
        name=data.name,
        email=email,
        password_hash=hash_password(data.password),
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "Registration successful",
        "role": role
    }


@router.post("/api/auth/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # Swagger OAuth2 uses "username".
    # We use the user's email as the username.
    email = form_data.username.strip().lower()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    if not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    token = create_token(
        user.id,
        user.role
    )

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        role=user.role,
        name=user.name,
    )

# VEHICLES - LIST
@router.get("/api/vehicles")
def list_vehicles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicles = db.query(Vehicle).all()

    return vehicles

# VEHICLES - CREATE
@router.post("/api/vehicles")
def create_vehicle(
    data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can add vehicles
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    vehicle = Vehicle(
        make=data.make,
        model=data.model,
        category=data.category,
        price=data.price,
        quantity=data.quantity,
    )

    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)

    return vehicle

# VEHICLES - SEARCH
@router.get("/api/vehicles/search")
def search_vehicles(
    make: str | None = None,
    model: str | None = None,
    category: str | None = None,
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Vehicle)

    if make:
        query = query.filter(
            Vehicle.make.ilike(f"%{make}%")
        )

    if model:
        query = query.filter(
            Vehicle.model.ilike(f"%{model}%")
        )

    if category:
        query = query.filter(
            Vehicle.category.ilike(f"%{category}%")
        )

    if min_price is not None:
        query = query.filter(
            Vehicle.price >= min_price
        )

    if max_price is not None:
        query = query.filter(
            Vehicle.price <= max_price
        )

    return query.all()

# VEHICLES - UPDATE
@router.put("/api/vehicles/{vehicle_id}")
def update_vehicle(
    vehicle_id: int,
    data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only admin can update vehicles
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    # Update only supplied fields
    if data.make is not None:
        vehicle.make = data.make

    if data.model is not None:
        vehicle.model = data.model

    if data.category is not None:
        vehicle.category = data.category

    if data.price is not None:
        vehicle.price = data.price

    if data.quantity is not None:
        vehicle.quantity = data.quantity

    db.commit()
    db.refresh(vehicle)

    return vehicle

# VEHICLES - DELETE
@router.delete("/api/vehicles/{vehicle_id}")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin only
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    db.delete(vehicle)
    db.commit()

    return {
        "message": "Vehicle deleted"
    }

# PURCHASE

@router.post("/api/vehicles/{vehicle_id}/purchase")
def purchase_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    if vehicle.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Vehicle is out of stock"
        )

    vehicle.quantity -= 1

    db.commit()
    db.refresh(vehicle)

    return {
        "message": "Vehicle purchased successfully",
        "vehicle": vehicle
    }


#RESTOCK
@router.post("/api/vehicles/{vehicle_id}/restock")
def restock_vehicle(
    vehicle_id: int,
    data: RestockRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin only
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )

    vehicle = (
        db.query(Vehicle)
        .filter(Vehicle.id == vehicle_id)
        .first()
    )

    if not vehicle:
        raise HTTPException(
            status_code=404,
            detail="Vehicle not found"
        )

    if data.quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Restock quantity must be greater than zero"
        )

    vehicle.quantity += data.quantity

    db.commit()
    db.refresh(vehicle)

    return {
        "message": "Vehicle restocked successfully",
        "vehicle": vehicle
    }