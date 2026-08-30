# Algerian E-Commerce — Backend API

REST API backend for the Algerian e-commerce platform, built with **FastAPI** (Python) + **SQLAlchemy** + **PostgreSQL**.

Deployed on Render: <https://backalgeriacommerce.onrender.com> (auto-generated docs at `/docs`).

## Tech Stack

- **Framework:** FastAPI (with Uvicorn)
- **ORM:** SQLAlchemy
- **Database:** PostgreSQL (17)
- **Image upload:** served statically from `uploads/`
- **Carrier credential encryption:** AES-256-GCM (`cryptography`)

## Requirements

- Python 3.12+
- PostgreSQL 17 (or use Docker Compose from the repository root)
- `pip`

## Getting Started (local)

### 1. Environment configuration

Copy the example environment file and fill in real values:

```bash
cp .env.example .env
```

Create a unique encryption key (64 hex chars = 32 random bytes):

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Then paste it into `.env` as `CREDENTIAL_ENCRYPTION_KEY`.

The `.env` file is **git-ignored and never committed**. Only `.env.example` (with placeholders) is tracked.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the server

```bash
uvicorn app.main:app --reload --port 8000
```

Navigate to <http://localhost:8000/docs> for the interactive API documentation.

## Running with Docker Compose

From the repository root of the full project, the backend runs alongside PostgreSQL and the frontend:

```bash
docker compose up --build
```

The backend is exposed on port `8000`.

## Environment Variables

| Variable | Description | Example |
| --- | --- | --- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg://postgres:postgres@db:5432/ecommerce` |
| `CREDENTIAL_ENCRYPTION_KEY` | 64-hex (32-byte) key used to encrypt carrier credentials (AES-256-GCM) | generated with `secrets.token_hex(32)` |
| `PORT` | Port the server listens on (set by the platform; defaults to `8000` locally) | `8000` |

> Note: the app automatically appends the `+psycopg` driver to `postgres://` URLs.

## API Endpoints

| Area | Base path | Description |
| --- | --- | --- |
| Products | `/products` | Product CRUD (with variants, options, tags) |
| Categories | `/categories` | Category CRUD |
| Orders | `/orders` | Order CRUD + status updates |
| Customers | `/customers` | Customer data |
| Dashboard | `/dashboard/stats` | Aggregate stats for the admin dashboard |
| Upload | `/upload/product-image` | Product image upload |
| Shipping | `/shipping/*` | Carrier connections + shipping providers |
| Static | `/uploads/*` | Served product images |

Full interactive docs: `/docs` (Swagger UI).

## Carriers & Credential Encryption

Shipping provider connections store API credentials. These credentials are **encrypted at rest** using AES-256-GCM with `CREDENTIAL_ENCRYPTION_KEY`. Do not rotate or change that key while real credentials exist, as it would make them undecryptable.

## Database Migrations

The app uses `Base.metadata.create_all()` to create tables on startup. Manual SQL migrations live in `migrations/` (see `migrations/README.md`) and are applied manually for schema changes on the deployed Render database.

## Project Structure

```
app/
  api/        # Route handlers (products, orders, categories, customers, dashboard, upload, shipping)
  core/       # Core configuration
  db/         # Database engine/session (database.py)
  models/     # SQLAlchemy models
  schemas/    # Pydantic schemas
  services/   # Business logic (image_service, credential_crypto, providers/)
  main.py     # FastAPI app entrypoint
  seed.py     # Seed script
migrations/   # Manual SQL migrations
uploads/      # Uploaded product images (git-ignored content)
```

## Security Notes

- `.env` and other local environment files are git-ignored; never commit real secrets.
- Only `.env.example` (placeholders) is tracked.
- Carrier credentials are encrypted before being stored.
