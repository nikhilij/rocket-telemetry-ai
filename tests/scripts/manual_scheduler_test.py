"""Manual scheduler test script.

Run this to simulate what the periodic Celery scheduler would do when
ANOMALY_SCHEDULE_ENABLED is true. It enumerates distinct (asset_id, metric)
pairs from recent telemetry (window = ANOMALY_WINDOW_SIZE_SECONDS) and invokes
anomaly detection directly (synchronously) without Celery infrastructure.

Usage (PowerShell):

  uvicorn app.main:app --reload  # in separate shell if API needed
  python tests/scripts/manual_scheduler_test.py

Ensure your database and Redis (if you want to compare Celery task behavior) are running.
"""

from app import crud, config
from app.db import SessionLocal
from app.worker import detect_anomalies


def main():
    db = SessionLocal()
    try:
        pairs = crud.get_distinct_asset_metric_pairs(
            db, window_seconds=config.ANOMALY_WINDOW_SIZE_SECONDS
        )
        if not pairs:
            print("No recent distinct (asset_id, metric) pairs found.")
            return
        print(f"Found {len(pairs)} distinct pairs: {pairs}")
        for asset_id, metric in pairs:
            result = detect_anomalies(asset_id, metric)  # direct call, not async
            print(f"Result for {asset_id}/{metric}: {result}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
