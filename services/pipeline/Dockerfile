FROM python:3.12-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Dev: src mounted as volume so edits don't require rebuild ─────────────────
FROM base AS dev
CMD ["python", "-m", "src.main"]

# ── Prod: bake source in; runs as an ECS scheduled task ───────────────────────
FROM base AS prod
COPY src/ ./src/
CMD ["python", "-m", "src.main"]
