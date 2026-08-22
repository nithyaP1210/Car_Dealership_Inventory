import os
from pathlib import Path

TEST_DB = Path(__file__).with_name("test.db")
if TEST_DB.exists():
    TEST_DB.unlink()
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB}"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def auth(email="test@example.com"):
    client.post(
        "/api/auth/register",
        json={"name": "Test User", "email": email, "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "password123"},
    )
    return response.json()["access_token"]


def test_register_and_login():
    token = auth()
    assert token


def test_duplicate_registration():
    response = client.post(
        "/api/auth/register",
        json={"name": "Another", "email": "test@example.com", "password": "password123"},
    )
    assert response.status_code == 400


def test_protected_endpoint_requires_token():
    response = client.get("/api/vehicles")
    assert response.status_code == 401


def test_create_search_update_vehicle():
    token = auth("vehicle@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/vehicles",
        headers=headers,
        json={
            "make": "Toyota",
            "model": "Camry",
            "category": "Sedan",
            "price": 32000,
            "quantity": 2,
        },
    )
    assert created.status_code == 200
    vehicle_id = created.json()["id"]

    search = client.get(
        "/api/vehicles/search?make=Toyota&min_price=30000",
        headers=headers,
    )
    assert search.status_code == 200
    assert len(search.json()) == 1

    updated = client.put(
        f"/api/vehicles/{vehicle_id}",
        headers=headers,
        json={
            "make": "Toyota",
            "model": "Corolla",
            "category": "Sedan",
            "price": 28000,
            "quantity": 2,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["model"] == "Corolla"


def test_purchase_decreases_quantity_and_zero_stock_fails():
    token = auth("purchase@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/vehicles",
        headers=headers,
        json={
            "make": "Honda",
            "model": "City",
            "category": "Sedan",
            "price": 18000,
            "quantity": 1,
        },
    )
    vehicle_id = created.json()["id"]

    purchase = client.post(
        f"/api/vehicles/{vehicle_id}/purchase",
        headers=headers,
    )
    assert purchase.status_code == 200
    assert purchase.json()["quantity"] == 0

    second_purchase = client.post(
        f"/api/vehicles/{vehicle_id}/purchase",
        headers=headers,
    )
    assert second_purchase.status_code == 400


def test_admin_can_restock_and_delete():
    # The first registered account (test@example.com) is the demo admin.
    response = client.post(
        "/api/auth/login",
        json={"email": "test@example.com", "password": "password123"},
    )
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/vehicles",
        headers=headers,
        json={
            "make": "BMW",
            "model": "X5",
            "category": "SUV",
            "price": 75000,
            "quantity": 1,
        },
    )
    vehicle_id = created.json()["id"]

    restock = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        headers=headers,
        json={"quantity": 2},
    )
    assert restock.status_code == 200
    assert restock.json()["quantity"] == 3

    deleted = client.delete(
        f"/api/vehicles/{vehicle_id}",
        headers=headers,
    )
    assert deleted.status_code == 200


def test_normal_user_cannot_restock_or_delete():
    token = auth("normal@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/vehicles",
        headers=headers,
        json={
            "make": "Kia",
            "model": "Seltos",
            "category": "SUV",
            "price": 25000,
            "quantity": 2,
        },
    )
    vehicle_id = created.json()["id"]

    restock = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        headers=headers,
        json={"quantity": 1},
    )
    assert restock.status_code == 403

    deleted = client.delete(
        f"/api/vehicles/{vehicle_id}",
        headers=headers,
    )
    assert deleted.status_code == 403
