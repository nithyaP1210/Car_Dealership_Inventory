import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# Isolated in-memory SQLite DB for tests — never touches dealership.db
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # keeps the same in-memory DB across connections
)

TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_database():
    """Fresh, empty tables before every single test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_token(client):
    """Registers the first user (becomes ADMIN) and returns a valid JWT."""
    client.post(
        "/api/auth/register",
        json={"name": "Admin User", "email": "admin@test.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "admin@test.com", "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def user_token(client, admin_token):
    """Registers a second user (becomes USER, since admin was registered first) and returns a valid JWT."""
    client.post(
        "/api/auth/register",
        json={"name": "Regular User", "email": "user@test.com", "password": "password123"},
    )
    response = client.post(
        "/api/auth/login",
        data={"username": "user@test.com", "password": "password123"},
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}
