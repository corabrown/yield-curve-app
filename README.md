# Yield Curve App

A full-stack application for visualizing US Treasury yield curves, built with FastAPI, Streamlit, PostgreSQL, and Docker.

## Requirements

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v4.x or later, which bundles Docker Compose v2.1+)

## Quick start

To bring up the entire stack in one command:

```bash
make up
```

Then open [http://localhost:8501](http://localhost:8501).

To tear everything down (including the database volume):

```bash
make down
```

---

## Step-by-step startup

If you want to bring up each stage individually, run these in order:

### 1. Start the database

```bash
make db
```

Starts PostgreSQL and waits until it is healthy.

### 2. Run migrations

```bash
make migrate
```

Applies all Flyway SQL migrations in `migrations/`. Safe to re-run — already-applied migrations are skipped.

### 3. Backfill historical data

```bash
make backfill
```

Fetches US Treasury yield curve data from FRED back to 2010-01-01 and loads it into the database. This takes a few minutes on first run. Idempotent — re-running skips already-loaded rows.

### 4. Start the API

```bash
make api
```

Starts the FastAPI server on [http://localhost:8000](http://localhost:8000). Docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 5. Start the frontend

```bash
make frontend
```

Starts the Streamlit app on [http://localhost:8501](http://localhost:8501).

---

## Other commands

| Command | Description |
|---|---|
| `make down` | Stop all services and delete the database volume |
| `make logs` | Tail logs for all services |
| `make api-logs` | Tail API logs |
| `make frontend-logs` | Tail frontend logs |
| `make run-pipeline` | Run the daily yield curve fetch (on demand) |
| `make shell-db` | Open a psql shell in the running database |
| `make shell-api` | Open a bash shell in the running API container |

## Services

| Service | Port | Description |
|---|---|---|
| `postgres` | 5432 | PostgreSQL database |
| `api` | 8000 | FastAPI backend |
| `frontend` | 8501 | Streamlit frontend |
