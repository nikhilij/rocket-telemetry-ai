"""
Celery worker for background tasks like anomaly detection.
"""

from celery import Celery
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np
import os
from datetime import timezone

from . import config, models, schemas, crud
from .db import SessionLocal

celery_app = Celery(
    "worker", broker=config.CELERY_BROKER_URL, backend=config.CELERY_RESULT_BACKEND
)

# Configure pool for Windows compatibility
celery_app.conf.update(worker_pool="solo" if os.name == "nt" else "prefork")


@celery_app.task(name="app.worker.detect_anomalies")
def detect_anomalies(asset_id: str, metric: str):
    """
    Analyzes recent telemetry for a given asset and metric to detect anomalies.
    """
    db: Session = SessionLocal()
    try:
        window_end = datetime.now(timezone.utc)
        window_start = window_end - timedelta(
            seconds=config.ANOMALY_WINDOW_SIZE_SECONDS
        )

        events = crud.get_telemetry_events_by_metric(
            db,
            asset_id=asset_id,
            metric=metric,
            start_time=window_start,
            end_time=window_end,
        )

        if len(events) < 10:  # Need a minimum number of data points
            return f"Not enough data points for {asset_id}/{metric} in the last window."

        values = np.array([event.value for event in events])
        mean = np.mean(values)
        std_dev = np.std(values)

        if std_dev == 0:  # Avoid division by zero
            return f"Standard deviation is zero for {asset_id}/{metric}."

        anomalies_detected = []
        for event in events:
            z_score = (event.value - mean) / std_dev
            if abs(z_score) > config.ANOMALY_Z_SCORE_THRESHOLD:
                explanation = (
                    f"Anomaly detected for {asset_id}/{metric}: "
                    f"Value {event.value} is {abs(z_score):.2f} standard deviations from the mean of {mean:.2f}."
                )
                anomaly_record = schemas.AnomalyRecordCreate(
                    telemetry_id=event.id,
                    asset_id=asset_id,
                    timestamp=event.timestamp,
                    metric=metric,
                    score=abs(z_score),
                    explanation=explanation,
                    details={
                        "mean": mean,
                        "std_dev": std_dev,
                        "window_size": len(values),
                    },
                )
                crud.create_anomaly_record(db, anomaly_record)
                anomalies_detected.append(explanation)

        if anomalies_detected:
            return (
                f"Detected {len(anomalies_detected)} anomalies for {asset_id}/{metric}."
            )

        return f"No anomalies detected for {asset_id}/{metric}."

    finally:
        db.close()
