# Yield Curve App

This full-stack application fetches and stores historical and up-to-date yield curve information in Postgres, exposes that data via a FastAPI, and creates a lightweight frontend using Streamlit. Users are able to view the current yield curve, historical yield curves for various tenors, create users, place orders under users, and view a user's historical orders. All backend data is stored in a Postgres instance and accessed via the api for display on the frontend. 

To deploy this stack in production on AWS, we would need to set up an RDS instance to host the historical data, a container to host the api, and a container to host the front-end. A daily refresh job could run on ECS or Lambda to fetch the most recent yield curve information and insert it into the database. We'd need constraints on date+tenor uniqueness in order to ensure we're not storing any duplicated data. 

## Improvements

The frontend could be improved to create a better user experience. I used Streamlit since it's a Python framework and was straightforward to get up and running. However, it has many limitations and makes for a clunky UI, especially on the "User" tab. The development experience could also be improved by storing the historical data in a dev db rather than rebuilding it each time you compose the docker containers. While this makes the dev experience self contained and requires no connections to any external services, it is not a sustainable pattern. 

## Requirements

You need Docker Engine and the Docker Compose plugin (v2.1+). Docker Desktop is one way to get both, but not required.

**Linux** — install Docker Engine and the Compose plugin directly:
```bash
curl -fsSL https://get.docker.com | sh
sudo apt-get install docker-compose-plugin   # Debian/Ubuntu
```

**Mac** — Docker Engine doesn't run natively on macOS, so you need a tool that manages the Linux VM for you. Options:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (official, most common)
- [OrbStack](https://orbstack.dev) (lighter weight, faster)
- [Colima](https://github.com/abiosoft/colima) (open source, CLI-only)

## Quick start

To bring up the entire stack in one command:

```bash
make up
```

This will take a view minutes as the docker compose performs a backfill of historical yield curve data going back to 2010. In production, such a backfill would only need to happen once (or on refresh schedule in case data is updated over time).

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

## Database connection

Default credentials (overridable via environment variables):

| Parameter | Default |
|---|---|
| Host | `localhost` |
| Port | `5432` |
| Database | `yieldcurve` |
| Username | `yieldcurve` |
| Password | `localpassword` |
