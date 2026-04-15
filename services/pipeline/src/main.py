"""
Entry point for the daily yield curve batch job.

Local:  docker compose run --rm pipeline   (or: make run-pipeline)
AWS:    ECS scheduled task triggered by EventBridge (daily)
"""

import logging
import sys
from datetime import date

from src.backfill import fetch_today
from src.loader import upsert_rates

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    stream=sys.stdout,
)
log = logging.getLogger(__name__)


def run() -> None:
    today = date.today()
    log.info("Pipeline starting for %s", today)

    records = fetch_today()
    log.info("Fetched %d rate records from FRED", len(records))

    if not records:
        log.warning("No records returned — FRED may not have published data yet.")
        return

    upsert_rates(records)
    log.info("Pipeline complete.")


if __name__ == "__main__":
    run()
