
# ── Full stack ────────────────────────────────────────────────────────────────
up:
	docker compose up --build -d

down:
	docker compose down -v

# ── Step-by-step (run in order) ───────────────────────────────────────────────
db:
	docker compose up -d postgres

migrate:
	docker compose run --rm migrations

backfill:
	docker compose run --rm --build backfill

api:
	docker compose up -d --build --no-deps api

frontend:
	docker compose up -d --build --no-deps frontend

# ── Logs ─────────────────────────────────────────────────────────────────────
logs:
	docker compose logs -f

api-logs:
	docker compose logs -f api

frontend-logs:
	docker compose logs -f frontend

pipeline-logs:
	docker compose logs -f pipeline
