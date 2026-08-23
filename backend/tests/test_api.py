"""
Backend test suite for the Car Dealership Inventory API.

Run with:
    pytest
    pytest -v                  (verbose, shows each test name)
    pytest --cov=app           (with coverage report)
"""


# ── AUTH: REGISTRATION ───────────────────────────────────────────

def test_first_registered_user_becomes_admin(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Admin User", "email": "admin@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "ADMIN"


def test_second_registered_user_becomes_regular_user(client):
    client.post(
        "/api/auth/register",
        json={"name": "Admin User", "email": "admin@test.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/register",
        json={"name": "Second User", "email": "second@test.com", "password": "password123"},
    )
    assert response.status_code == 201
    assert response.json()["role"] == "USER"


def test_cannot_register_duplicate_email(client):
    client.post(
        "/api/auth/register",
        json={"name": "First", "email": "dupe@test.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/register",
        json={"name": "Second", "email": "dupe@test.com", "password": "password123"},
    )
    assert response.status_code == 400


def test_registration_rejects_short_password(client):
    response = client.post(
        "/api/auth/register",
        json={"name": "Test", "email": "short@test.com", "password": "123"},
    )
    assert response.status_code == 422


# ── AUTH: LOGIN ───────────────────────────────────────────────────

def test_login_with_correct_credentials(client):
    client.post(
        "/api/auth/register",
        json={"name": "Admin", "email": "admin@test.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@test.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["role"] == "ADMIN"


def test_login_with_wrong_password_fails(client):
    client.post(
        "/api/auth/register",
        json={"name": "Admin", "email": "admin@test.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@test.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_with_unknown_email_fails(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "nobody@test.com", "password": "password123"},
    )
    assert response.status_code == 401


# ── VEHICLES: ACCESS CONTROL ──────────────────────────────────────

def test_list_vehicles_requires_authentication(client):
    response = client.get("/api/vehicles")
    assert response.status_code == 401


def test_admin_can_create_vehicle(client, admin_headers):
    response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["make"] == "Toyota"
    assert body["id"] is not None


def test_regular_user_cannot_create_vehicle(client, user_headers):
    response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=user_headers,
    )
    assert response.status_code == 403


def test_regular_user_can_list_vehicles(client, admin_headers, user_headers):
    client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    response = client.get("/api/vehicles", headers=user_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


# ── VEHICLES: CRUD ─────────────────────────────────────────────────

def test_update_vehicle(client, admin_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/vehicles/{vehicle_id}",
        json={"make": "Toyota", "model": "Camry 2026", "category": "Sedan", "price": 35000, "quantity": 5},
        headers=admin_headers,
    )
    assert update_response.status_code == 200
    body = update_response.json()
    assert body["model"] == "Camry 2026"
    assert body["price"] == 35000


def test_regular_user_cannot_update_vehicle(client, admin_headers, user_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.put(
        f"/api/vehicles/{vehicle_id}",
        json={"make": "Toyota", "model": "Hacked", "category": "Sedan", "price": 1, "quantity": 5},
        headers=user_headers,
    )
    assert response.status_code == 403


def test_update_nonexistent_vehicle_returns_404(client, admin_headers):
    response = client.put(
        "/api/vehicles/9999",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    assert response.status_code == 404


def test_admin_can_delete_vehicle(client, admin_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Honda", "model": "City", "category": "Sedan", "price": 18000, "quantity": 3},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/vehicles/{vehicle_id}", headers=admin_headers)
    assert delete_response.status_code == 200

    list_response = client.get("/api/vehicles", headers=admin_headers)
    assert len(list_response.json()) == 0


def test_regular_user_cannot_delete_vehicle(client, admin_headers, user_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Honda", "model": "City", "category": "Sedan", "price": 18000, "quantity": 3},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.delete(f"/api/vehicles/{vehicle_id}", headers=user_headers)
    assert response.status_code == 403


def test_delete_nonexistent_vehicle_returns_404(client, admin_headers):
    response = client.delete("/api/vehicles/9999", headers=admin_headers)
    assert response.status_code == 404


# ── VEHICLES: SEARCH ─────────────────────────────────────────────

def test_search_by_make(client, admin_headers):
    client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    client.post(
        "/api/vehicles",
        json={"make": "Skoda", "model": "Rapid", "category": "Sedan", "price": 720000, "quantity": 3},
        headers=admin_headers,
    )

    response = client.get("/api/vehicles/search?make=Toyota", headers=admin_headers)
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["make"] == "Toyota"


def test_search_by_price_range(client, admin_headers):
    client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    client.post(
        "/api/vehicles",
        json={"make": "Skoda", "model": "Rapid", "category": "Sedan", "price": 720000, "quantity": 3},
        headers=admin_headers,
    )

    response = client.get("/api/vehicles/search?min_price=500000", headers=admin_headers)
    results = response.json()
    assert len(results) == 1
    assert results[0]["make"] == "Skoda"


def test_search_with_no_matches_returns_empty_list(client, admin_headers):
    response = client.get("/api/vehicles/search?make=Ferrari", headers=admin_headers)
    assert response.status_code == 200
    assert response.json() == []


# ── VEHICLES: PURCHASE ────────────────────────────────────────────

def test_purchase_decreases_quantity_by_one(client, admin_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.post(f"/api/vehicles/{vehicle_id}/purchase", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["vehicle"]["quantity"] == 4


def test_regular_user_can_purchase(client, admin_headers, user_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 5},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.post(f"/api/vehicles/{vehicle_id}/purchase", headers=user_headers)
    assert response.status_code == 200


def test_cannot_purchase_out_of_stock_vehicle(client, admin_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Toyota", "model": "Camry", "category": "Sedan", "price": 32000, "quantity": 1},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    client.post(f"/api/vehicles/{vehicle_id}/purchase", headers=admin_headers)  # quantity now 0
    response = client.post(f"/api/vehicles/{vehicle_id}/purchase", headers=admin_headers)  # should fail
    assert response.status_code == 400


def test_purchase_nonexistent_vehicle_returns_404(client, admin_headers):
    response = client.post("/api/vehicles/9999/purchase", headers=admin_headers)
    assert response.status_code == 404


# ── VEHICLES: RESTOCK ──────────────────────────────────────────────

def test_admin_can_restock(client, admin_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Skoda", "model": "Rapid", "category": "Sedan", "price": 720000, "quantity": 3},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        json={"quantity": 5},
        headers=admin_headers,
    )
    assert response.status_code == 200
    assert response.json()["vehicle"]["quantity"] == 8


def test_regular_user_cannot_restock(client, admin_headers, user_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Skoda", "model": "Rapid", "category": "Sedan", "price": 720000, "quantity": 3},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        json={"quantity": 5},
        headers=user_headers,
    )
    assert response.status_code == 403


def test_restock_rejects_zero_or_negative_quantity(client, admin_headers):
    create_response = client.post(
        "/api/vehicles",
        json={"make": "Skoda", "model": "Rapid", "category": "Sedan", "price": 720000, "quantity": 3},
        headers=admin_headers,
    )
    vehicle_id = create_response.json()["id"]

    response = client.post(
        f"/api/vehicles/{vehicle_id}/restock",
        json={"quantity": 0},
        headers=admin_headers,
    )
    assert response.status_code == 422
