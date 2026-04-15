up:
	docker compose up --build -d

down:
	docker compose down -v

logs:
	docker compose logs -f

api-logs:
	docker compose logs -f api

frontend-logs:
	docker compose logs -f frontend

pipeline-logs:
	docker compose logs -f pipeline

run-pipeline:
	docker compose run --rm --build pipeline

backfill:
	docker compose run --rm --build pipeline python -m src.backfill

migrate:
	docker compose run --rm migrations

