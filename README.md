# Car Dealership Inventory System

This is a full-stack inventory app for a car dealership — built as a TDD kata assignment. Backend is FastAPI + SQLite, frontend is React + Tailwind. It handles user login/registration with two roles (Admin and regular User), lets admins manage the vehicle inventory, and lets any logged-in user browse, search, and "purchase" vehicles.

## Tech Stack

**Backend:** FastAPI, SQLAlchemy, SQLite, JWT (python-jose), Pydantic
**Frontend:** React, Vite, Tailwind CSS
**Testing:** pytest, httpx, pytest-cov

## Features

- Register/login with JWT auth
- First person to register becomes ADMIN automatically, everyone after that is a regular USER
- Admins can add, edit, delete, and restock vehicles
- Anyone logged in can browse, search, and purchase vehicles
- Search/filter by make, model, category, price range
- Purchase button disables itself once a vehicle hits zero stock

## Project Structure

```
car-dealership-inventory/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app entrypoint
│   │   ├── routers.py       # All API routes
│   │   ├── schemas.py       # Pydantic request/response models
│   │   ├── models.py        # SQLAlchemy ORM models
│   │   ├── database.py      # DB engine/session setup
│   │   ├── auth.py          # Password hashing, JWT creation
│   │   └── dependencies.py  # get_current_user auth dependency
│   ├── tests/
│   │   ├── conftest.py      # Pytest fixtures (isolated in-memory test DB)
│   │   └── test_api.py      # Full API test suite (27 tests)
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── README.md
└── PROMPTS.md
```

## Setup & Running Locally

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Interactive docs (Swagger) at `http://127.0.0.1:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

### Running Tests

```bash
cd backend
pytest -v
```

To include a coverage report:

```bash
pytest -v --cov=app
```

## API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/api/auth/register` | — | Register a new user |
| POST | `/api/auth/login` | — | Log in, returns JWT |
| GET | `/api/vehicles` | Any user | List all vehicles |
| POST | `/api/vehicles` | Admin | Add a vehicle |
| GET | `/api/vehicles/search` | Any user | Search/filter vehicles |
| PUT | `/api/vehicles/{id}` | Admin | Update a vehicle |
| DELETE | `/api/vehicles/{id}` | Admin | Delete a vehicle |
| POST | `/api/vehicles/{id}/purchase` | Any user | Purchase (decrease quantity) |
| POST | `/api/vehicles/{id}/restock` | Admin | Restock (increase quantity) |

## Test Report

27 tests, all passing. Covers registration, login, JWT auth, the full vehicle CRUD, search filters, purchase/restock (including out-of-stock and bad-quantity edge cases), and permission checks for both roles.

```
==================== test session starts ====================
platform win32 -- Python 3.13.3, pytest-8.4.1, pluggy-1.6.0
collected 27 items

tests/test_api.py::test_first_registered_user_becomes_admin PASSED
tests/test_api.py::test_second_registered_user_becomes_regular_user PASSED
tests/test_api.py::test_cannot_register_duplicate_email PASSED
tests/test_api.py::test_registration_rejects_short_password PASSED
tests/test_api.py::test_login_with_correct_credentials PASSED
tests/test_api.py::test_login_with_wrong_password_fails PASSED
tests/test_api.py::test_login_with_unknown_email_fails PASSED
tests/test_api.py::test_list_vehicles_requires_authentication PASSED
tests/test_api.py::test_admin_can_create_vehicle PASSED
tests/test_api.py::test_regular_user_cannot_create_vehicle PASSED
tests/test_api.py::test_regular_user_can_list_vehicles PASSED
tests/test_api.py::test_update_vehicle PASSED
tests/test_api.py::test_regular_user_cannot_update_vehicle PASSED
tests/test_api.py::test_update_nonexistent_vehicle_returns_404 PASSED
tests/test_api.py::test_admin_can_delete_vehicle PASSED
tests/test_api.py::test_regular_user_cannot_delete_vehicle PASSED
tests/test_api.py::test_delete_nonexistent_vehicle_returns_404 PASSED
tests/test_api.py::test_search_by_make PASSED
tests/test_api.py::test_search_by_price_range PASSED
tests/test_api.py::test_search_with_no_matches_returns_empty_list PASSED
tests/test_api.py::test_purchase_decreases_quantity_by_one PASSED
tests/test_api.py::test_regular_user_can_purchase PASSED
tests/test_api.py::test_cannot_purchase_out_of_stock_vehicle PASSED
tests/test_api.py::test_purchase_nonexistent_vehicle_returns_404 PASSED
tests/test_api.py::test_admin_can_restock PASSED
tests/test_api.py::test_regular_user_cannot_restock PASSED
tests/test_api.py::test_restock_rejects_zero_or_negative_quantity PASSED

=============== 27 passed in 8.23s ================
```

## Screenshots

_[Add screenshots here: login page, register page, vehicle dashboard (admin view), vehicle dashboard (user view), search results, add/edit vehicle form]_

## My AI Usage

I used Claude (Anthropic) through the claude.ai chat interface for most of this project. Full raw chat log is in `PROMPTS.md` at the repo root.

**What I actually used it for:**

I built the backend and frontend mostly on my own first, then leaned on Claude heavily once I got to the testing/debugging phase, since that's where I got stuck. I went through every endpoint manually in Swagger with Claude walking me through it step by step — register, login, list, search, update, delete, purchase, restock. A few things that looked like backend bugs at first turned out to just be me messing up the testing (submitting Swagger's placeholder text by accident, double-clicking Execute and doubling up a purchase/restock). Claude had me check the raw uvicorn terminal logs each time, which is how we actually figured out what was going on instead of guessing.

The most useful catch was a real bug: my frontend's login function was sending JSON with an `email` field, but my backend's login route uses FastAPI's OAuth2PasswordRequestForm, which needs form-urlencoded data with a `username` field instead. That's why login worked fine in Swagger but would've silently broken on the actual site. Claude spotted the mismatch and fixed just that one function.

I also had Claude write the pytest suite for me (I hadn't written backend tests before), covering auth, all the vehicle CRUD, search, purchase, restock, and the admin-vs-user permission checks — 27 tests total. One of the generated tests failed at first (expected a 400 on a bad restock quantity, got a 422 instead), and it turned out the test was wrong, not the code — my Pydantic schema already validates quantity > 0 before the route logic even runs, so FastAPI rejects it earlier with a 422. Fixed the test assertion once that was clear.

Claude also helped me draft this README and pointed out gaps in what I'd need for the actual submission (AI usage section, PROMPTS.md, the TDD requirement) that I hadn't fully read into the brief.

**Honest reflection:**

This wasn't really Test-Driven Development in the way the brief describes it. I built the features first and added tests afterward with Claude's help, rather than writing a failing test before each piece of code (red-green-refactor). I'm saying that plainly here instead of trying to dress it up — I understand that's a real gap against what was asked for, and if I did this again I'd write the failing test first for each endpoint before touching the implementation.

AI was genuinely useful for debugging faster than I could've on my own, especially the login bug, since that would've taken me a while to catch by just staring at the browser. But it also means a good chunk of this codebase and all of the tests were AI-assisted rather than written solo, which I'd rather be upfront about than pretend otherwise.



