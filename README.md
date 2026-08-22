# Car Dealership Inventory System

A simple full-stack Car Dealership Inventory System built for the TDD Kata.

## Features

- User registration and login
- JWT token authentication
- SQLite persistent database
- Protected vehicle APIs
- Vehicle search by make, model, category and price range
- Purchase decreases stock
- Purchase button is disabled when stock is zero
- Admin-only delete and restock
- Admin add and update vehicle UI
- React single-page frontend
- Tailwind CSS responsive styling
- Automated pytest backend tests
- Git/TDD workflow
- Transparent AI usage documentation

## Technology Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- JWT
- pytest

### Frontend
- React
- Vite
- Tailwind CSS
- HTML5/CSS3

## Project Structure

```text
backend/     FastAPI REST API, database and tests
frontend/    React + Tailwind SPA
screenshots/ Final application screenshots
PROMPTS.md   Raw AI prompts/chat log documentation
```

## API Endpoints

| Method | Endpoint | Access |
|---|---|---|
| POST | `/api/auth/register` | Public |
| POST | `/api/auth/login` | Public |
| POST | `/api/vehicles` | Authenticated |
| GET | `/api/vehicles` | Authenticated |
| GET | `/api/vehicles/search` | Authenticated |
| PUT | `/api/vehicles/{id}` | Authenticated |
| DELETE | `/api/vehicles/{id}` | Admin |
| POST | `/api/vehicles/{id}/purchase` | Authenticated |
| POST | `/api/vehicles/{id}/restock` | Admin |

## Database

The project uses SQLite stored in `backend/dealership.db`. This is a persistent database file and is not an in-memory database.

## Authentication

Registration and login are implemented with JWT token authentication.

For simple evaluation, the first registered account is assigned the `ADMIN` role. Later accounts are normal `USER` accounts. This makes it easy to demonstrate both admin and normal-user functionality.

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

Backend:

`http://localhost:8000`

Swagger API documentation:

`http://localhost:8000/docs`

## Frontend Setup

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend:

`http://localhost:5173`

## Running Tests

From the backend directory:

```bash
pytest -v
```

For coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

## TDD Approach

The backend was developed using a Red-Green-Refactor approach.

1. Tests were written first for the required behavior.
2. The tests initially failed because the corresponding implementation did not exist.
3. The minimum implementation was added to make the tests pass.
4. The implementation was then cleaned up and manually verified.
5. Git commits document the test and implementation stages.

The main tested behaviors include:

- Registration and login
- Duplicate registration
- Protected endpoints
- Vehicle creation
- Vehicle search
- Vehicle update
- Vehicle purchase
- Out-of-stock purchase rejection
- Admin restocking
- Admin deletion
- Normal-user restriction for admin operations

## Test Report

Run:

```bash
pytest -v
```

Then copy the actual terminal result here before submission.

Example format:

```text
Tests passed: 7
Tests failed: 0
```

Do not claim a test count that was not actually run.

## Screenshots

Add final screenshots to the `screenshots/` directory and reference them here.

Recommended screenshots:

1. Login/Register screen
2. Vehicle dashboard
3. Search/filter results
4. Admin controls
5. Swagger API documentation
6. Passing pytest output

## My AI Usage

### Tool Used

I used ChatGPT as an AI development assistant.

### How I Used AI

I used ChatGPT to:

- plan a simple architecture that satisfied the assignment requirements
- discuss REST API endpoint design
- create an initial TDD test plan
- generate initial boilerplate code
- help debug errors during implementation
- review the project against the assignment requirements
- suggest simple React and Tailwind UI structure
- help prepare README documentation

I manually reviewed and tested the generated suggestions and changed code when necessary.

### Reflection

AI reduced the time needed to create repetitive boilerplate and helped identify missing requirements. It was particularly useful for creating test cases and checking that the API and frontend covered the assignment.

I did not treat AI output as automatically correct. I ran the application, tested the API, ran the test suite, and manually reviewed the implementation.

## Git Workflow

The project uses small, descriptive commits. TDD commits show the test-first development process.

Example:

```text
test: add authentication tests
feat: implement authentication
test: add vehicle inventory tests
feat: implement vehicle inventory
feat: implement React dashboard
docs: add README and AI usage documentation
```

For commits where AI was used, the commit message includes the required AI co-author trailer.

## AI Prompt Log

Raw AI prompts and responses used during development are documented in `PROMPTS.md` as required by the assignment.

## Future Improvements

- PostgreSQL for production
- Refresh tokens
- Better role management
- Vehicle images
- Deployment
- Pagination
- Advanced inventory reporting
