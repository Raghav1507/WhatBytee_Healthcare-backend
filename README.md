# Healthcare Backend API

A production-structured **Django + Django REST Framework + PostgreSQL** backend for a
healthcare application. Users register with JWT authentication and manage patient,
doctor, and patient-doctor mapping records through a secure, validated REST API.

> **Try it instantly** — after setup, open **`http://127.0.0.1:8000/test/`** for an
> interactive browser console (signup → login → manage records, no Postman needed).

---

## Table of Contents

- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Interactive Test Console](#interactive-test-console)
- [Response Format](#response-format)
- [Error Handling](#error-handling)
- [Security Design](#security-design)
- [Running Tests](#running-tests)
- [Postman Collection](#postman-collection)
- [Deployment Notes](#deployment-notes)

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone <your-repo-url> healthcare_backend
cd healthcare_backend

# 2. Virtual environment + dependencies
python -m venv .venv
.venv\Scripts\activate          # Windows (use: source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env            # then edit .env with your DB credentials / SECRET_KEY

# 4. Start PostgreSQL + migrate
docker compose up -d
python manage.py migrate

# 5. (Optional) create an admin user for /admin
python scripts/create_superuser.py

# 6. Run the server
python manage.py runserver
```

Then open:

| URL | What you get |
|-----|--------------|
| **http://127.0.0.1:8000/test/** | ⭐ Interactive browser test console |
| http://127.0.0.1:8000/ | API index (list of all endpoints) |
| http://127.0.0.1:8000/api/health/ | Health check (`{"status":"healthy"}`) |
| http://127.0.0.1:8000/admin/ | Django admin (visual DB browser) |

---

## Tech Stack

| Layer        | Technology                                              |
|--------------|---------------------------------------------------------|
| Framework    | Django 6.x                                              |
| API          | Django REST Framework 3.x                               |
| Auth         | `djangorestframework-simplejwt` (JWT, Bearer tokens)    |
| Database     | PostgreSQL (`psycopg2-binary`)                          |
| Config       | `django-environ` (12-factor environment variables)      |
| Tests        | DRF `APITestCase` suite (49 tests)                      |

---

## Features

- **JWT authentication** — register, login, token refresh, logout, profile.
- **Custom User model** — email-based login (no username), UUID primary keys.
- **Patient management** — full CRUD, scoped to the authenticated owner.
- **Doctor management** — full CRUD with specialization / license validation.
- **Patient-doctor mappings** — assign, list, lookup by patient, remove.
- **Interactive browser console** — test the whole API at `/test/` without Postman.
- **Health check + API index** — `/api/health/` and `/` for quick discovery.
- **Consistent JSON envelope** — every response uses the same `success`/`data` shape.
- **Centralized exception handling** — uniform error codes for every failure.
- **Validation** — field-level and object-level validation on every write.
- **Pagination** — page-number pagination with adjustable `page_size` (max 100).
- **Throttling** — anon/user rate limits, stricter limits on auth endpoints.
- **Multi-environment settings** — `development` / `production` / `test`.
- **Dockerized PostgreSQL** — one command to spin up the database locally.

---

## Project Structure

```
healthcare_backend/
├── config/                     # Project-level configuration
│   ├── settings/
│   │   ├── base.py             # Shared settings (env-driven)
│   │   ├── development.py      # Local dev settings
│   │   ├── production.py       # Hardened production settings
│   │   └── test.py             # Fast in-memory test settings
│   ├── urls.py                 # Root URL configuration
│   ├── wsgi.py / asgi.py
│   └── bootstrap.py            # Loads .env before settings import
├── apps/
│   ├── users/                  # Custom User + auth endpoints
│   ├── patients/               # Patient model, serializers, views
│   ├── doctors/                # Doctor model, serializers, views
│   └── mappings/               # Patient-doctor mapping logic
├── core/                       # Shared utilities
│   ├── views.py                # API index, health check, test console
│   ├── exceptions.py           # Global exception handler + envelope
│   ├── pagination.py           # Enveloped pagination
│   ├── permissions.py          # Owner-based object permissions
│   └── validators.py           # Shared field validators
├── templates/
│   └── api_tester.html         # Interactive browser test console
├── scripts/
│   ├── smoke_test.py           # End-to-end live API test
│   └── create_superuser.py     # Create an admin user
├── postman_collection.json     # Importable Postman collection
├── docker-compose.yml          # Local PostgreSQL
├── pyproject.toml              # Ruff lint config
├── requirements.txt
├── .env / .env.example
└── manage.py
```

---

## Getting Started

### 1. Prerequisites

- Python 3.12+
- Docker (for the local PostgreSQL container) — *or* a local PostgreSQL install

### 2. Clone & create a virtual environment

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# then edit .env with your own SECRET_KEY and database credentials
```

### 5. Start PostgreSQL

**Option A — Docker (recommended):**

```bash
docker compose up -d
```

If port `5432` is already in use on your machine, map a different host port:

```bash
DB_PORT=5433 docker compose up -d
```

(then set `DB_PORT=5433` in `.env` as well)

**Option B — local PostgreSQL:** create a database and user matching `.env`.

### 6. Apply migrations & create an admin (optional)

```bash
python manage.py migrate
python scripts/create_superuser.py
```

### 7. Run the development server

```bash
python manage.py runserver
```

The API is now available at `http://127.0.0.1:8000`.

---

## Environment Variables

All sensitive configuration is read from environment variables (never hard-coded).

| Variable                 | Description                              | Default                       |
|--------------------------|------------------------------------------|-------------------------------|
| `DJANGO_ENV`             | `development` / `production` / `test`    | `development`                 |
| `SECRET_KEY`             | Django secret key                        | insecure dev fallback         |
| `DEBUG`                  | Debug mode                               | `True`                        |
| `ALLOWED_HOSTS`          | Comma-separated host allow-list          | `localhost,127.0.0.1`         |
| `DB_NAME`                | PostgreSQL database name                 | `healthcare_db`               |
| `DB_USER`                | PostgreSQL user                          | `postgres`                    |
| `DB_PASSWORD`            | PostgreSQL password                      | —                             |
| `DB_HOST`                | PostgreSQL host                          | `localhost`                   |
| `DB_PORT`                | PostgreSQL port                          | `5432`                        |
| `ACCESS_TOKEN_LIFETIME`  | Access token lifetime (minutes)          | `15`                          |
| `REFRESH_TOKEN_LIFETIME` | Refresh token lifetime (days)            | `7`                           |
| `CORS_ALLOWED_ORIGINS`   | Comma-separated frontend origins         | `localhost:3000,5173`         |

> `.gitignore` excludes `.env`, so real secrets are never committed. Use
> `.env.example` as the template.

---

## API Reference

All endpoints are prefixed with `/api`. Authenticated endpoints require the header:

```
Authorization: Bearer <access_token>
```

### 0. Utility (no auth)

| Method | Endpoint           | Description                                  |
|--------|--------------------|----------------------------------------------|
| GET    | `/`                | API index — lists every endpoint group       |
| GET    | `/api/health/`     | Health check (verifies DB connectivity)      |
| GET    | `/test/`           | Interactive browser test console (HTML)      |
| GET    | `/admin/`          | Django admin site                            |

**Health check response**

```json
GET /api/health/
{ "status": "healthy", "database": "up" }
```

### 1. Authentication

| Method | Endpoint                    | Auth | Description                         |
|--------|-----------------------------|------|-------------------------------------|
| POST   | `/api/auth/register/`       | No   | Register a new user                 |
| POST   | `/api/auth/login/`          | No   | Log in, returns JWT pair            |
| POST   | `/api/auth/token/refresh/`  | No   | Exchange refresh token for access   |
| POST   | `/api/auth/logout/`         | Yes  | Blacklist a refresh token           |
| GET    | `/api/auth/me/`             | Yes  | Current user's profile              |

**Register**

```http
POST /api/auth/register/
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "Str0ngPass!23",
  "password2": "Str0ngPass!23",
  "phone": "+1 555 0100"
}
```

**Login**

```http
POST /api/auth/login/
Content-Type: application/json

{ "email": "john@example.com", "password": "Str0ngPass!23" }
```

Response:

```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "access": "<jwt-access-token>",
    "refresh": "<jwt-refresh-token>",
    "user": { "id": "...", "name": "John Doe", "email": "john@example.com" }
  }
}
```

### 2. Patient Management *(authenticated)*

| Method | Endpoint               | Description                                  |
|--------|------------------------|----------------------------------------------|
| POST   | `/api/patients/`       | Add a patient (owned by the requester)       |
| GET    | `/api/patients/`       | List **your** patients (`?search=`, paging)  |
| GET    | `/api/patients/<id>/`  | Patient detail (includes assigned doctors)   |
| PUT    | `/api/patients/<id>/`  | Full update                                  |
| PATCH  | `/api/patients/<id>/`  | Partial update                               |
| DELETE | `/api/patients/<id>/`  | Delete a patient                             |

**Create patient**

```json
POST /api/patients/
{
  "name": "Jane Patient",
  "age": 34,
  "gender": "female",
  "phone": "+1 555 2233",
  "email": "jane@example.com",
  "address": "12 Grove Street",
  "medical_history": "Asthma"
}
```

`gender` must be one of: `male`, `female`, `other`, `prefer_not_to_say`.

### 3. Doctor Management *(authenticated)*

| Method | Endpoint              | Description                                |
|--------|-----------------------|--------------------------------------------|
| POST   | `/api/doctors/`       | Add a doctor                               |
| GET    | `/api/doctors/`       | List doctors (`?search=`, `?specialization=`) |
| GET    | `/api/doctors/<id>/`  | Doctor detail (includes patient count)     |
| PUT    | `/api/doctors/<id>/`  | Full update                                |
| PATCH  | `/api/doctors/<id>/`  | Partial update                             |
| DELETE | `/api/doctors/<id>/`  | Delete a doctor                            |

**Create doctor**

```json
POST /api/doctors/
{
  "name": "Sarah House",
  "specialization": "Cardiology",
  "email": "s.house@example.com",
  "phone": "+1 555 9999",
  "license_number": "LIC-9001",
  "years_of_experience": 14,
  "hospital": "City General"
}
```

### 4. Patient-Doctor Mappings *(authenticated)*

| Method | Endpoint                    | Description                                    |
|--------|-----------------------------|------------------------------------------------|
| POST   | `/api/mappings/`            | Assign a doctor to a patient                   |
| GET    | `/api/mappings/`            | List all mappings you can access               |
| GET    | `/api/mappings/<patient_id>/` | All doctors assigned to a specific patient   |
| DELETE | `/api/mappings/<id>/`       | Remove a doctor from a patient                 |

> **Note:** `GET` interprets the path parameter as a **patient id**, while
> `DELETE` interprets it as a **mapping id** — matching the spec's two routes
> on the same URL shape.

**Assign a doctor**

```json
POST /api/mappings/
{
  "patient": "<patient-uuid>",
  "doctor": "<doctor-uuid>",
  "notes": "Annual check-up"
}
```

**Doctors for a patient**

```http
GET /api/mappings/<patient_id>/
```

```json
{
  "success": true,
  "message": "OK",
  "data": {
    "patient_id": "…",
    "patient_name": "Jane Patient",
    "assigned_doctors": [
      {
        "id": "…",
        "doctor": { "id": "…", "name": "Sarah House", "specialization": "Cardiology", … },
        "notes": "Annual check-up",
        "assigned_at": "…"
      }
    ],
    "count": 1
  }
}
```

---

## Interactive Test Console

Open **`http://127.0.0.1:8000/test/`** after starting the server. It's a
self-contained HTML page (no build step, no Postman) with four panels:

| Panel | Actions |
|-------|---------|
| **1 · Sign Up / Log In** | Register a new account or log in; the JWT is stored automatically |
| **2 · Patients** | Create, list, and delete patients |
| **3 · Doctors** | Create, list, and delete doctors |
| **4 · Assign Doctor → Patient** | Pick a patient + doctor and assign / unassign |

Every request/response is shown as pretty-printed JSON in the **Response Output**
panel, so you can see exactly what the API returns.

**How to use it:**
1. Open `/test/`, keep the prefilled values in panel 1 → **Sign Up**, then **Log In**.
2. Panel 2 → **Create Patient** → **Refresh List**.
3. Panel 3 → **Create Doctor** → **Refresh List**.
4. Panel 4 → select the patient and doctor → **Assign**.

> The page stores the JWT in `localStorage`, so your session survives page
> reloads. Clear site data to log out.

---

## Response Format

Every endpoint returns the same envelope.

**Success**

```json
{ "success": true, "message": "…", "data": { … } }
```

**Paginated list**

```json
{
  "success": true,
  "message": "OK",
  "data": { "count": 25, "next": "…", "previous": null, "results": [ … ] }
}
```

**Error**

```json
{
  "success": false,
  "error": {
    "code": "validation_error",
    "message": "Invalid input provided.",
    "details": { "age": ["Age must be between 0 and 150."] }
  }
}
```

---

## Error Handling

A single DRF exception handler (`core/exceptions.py`) converts every failure into
the envelope above with a stable machine-readable `code`:

| HTTP | Code                   | When                                          |
|------|------------------------|-----------------------------------------------|
| 400  | `validation_error`     | Field validation failed                       |
| 400  | `bad_request`          | Malformed payload / missing required field   |
| 401  | `authentication_failed`| Missing, invalid, or expired JWT             |
| 403  | `permission_denied`    | Authenticated but not allowed (e.g. mapping) |
| 404  | `not_found`            | Missing record **or** not owned by you       |
| 429  | `rate_limited`         | Throttle limit exceeded                      |
| 500  | `api_error`            | Unexpected server error (logged, not leaked) |

---

## Security Design

- **Passwords** are hashed with Django's PBKDF2 and validated (min length 8,
  common-password and similarity checks).
- **JWT** access tokens are short-lived (15 min default) with rotating refresh
  tokens (7 days default).
- **Ownership scoping** — patient and doctor querysets are filtered to
  `created_by = request.user`, so other users' records return `404` rather than
  leaking their existence.
- **Object-level permissions** (`IsOwnerOrReadOnly`) block writes to records you
  do not own as defense-in-depth.
- **Mapping safety** — you can only assign doctors to patients you created, and
  a unique constraint prevents duplicate assignments.
- **Throttling** — stricter `auth` scope (10/min) on login/register; general
  anon (20/min) and user (120/min) limits.
- **Secrets** live only in environment variables; `.env` is git-ignored.
- **Production settings** enable HSTS-ready, cookie-secure, and XSS/sniffing
  protections.

---

## Running Tests

**Unit / integration tests** (in-memory SQLite, fast):

```bash
python manage.py test --settings=config.settings.test
```

**End-to-end smoke test** (requires a running server + PostgreSQL):

```bash
# terminal 1
python manage.py runserver

# terminal 2
python scripts/smoke_test.py
```

The smoke suite drives all 14 required endpoints live and prints a PASS/FAIL
summary (25 checks).

**Linting** (Ruff, configured in `pyproject.toml`):

```bash
pip install ruff
ruff check .
```

---

## Postman Collection

Import [`postman_collection.json`](./postman_collection.json) into Postman.

1. Run **Login** (or **Register**) — the test script automatically saves the
   `access_token` and `refresh_token` into collection variables.
2. Run **Create Patient** / **Create Doctor** — IDs are saved automatically.
3. Use **Assign Doctor to Patient** and the remaining mapping requests.

All authenticated requests use `Authorization: Bearer {{access_token}}`.

---

## Deployment Notes

- Set `DJANGO_ENV=production` and provide a strong `SECRET_KEY`,
  `ALLOWED_HOSTS`, and database credentials via your host's environment.
- Run behind a reverse proxy (Nginx) with Gunicorn:
  `gunicorn config.wsgi:application --bind 0.0.0.0:8000`.
- Serve static files with a CDN or `whitenoise` (`python manage.py collectstatic`).
- Enable `django-cors-headers` (already listed in `requirements.txt`) once a
  frontend is connected, and keep `CORS_ALLOWED_ORIGINS` explicit.
- Consider adding the simplejwt blacklist app if you need true server-side
  refresh-token revocation.

---

## License

This project is provided as a portfolio/assignment backend. Adapt it freely for
your own use.
