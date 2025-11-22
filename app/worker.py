"""
Celery worker for background tasks like anomaly detection.
"""

from celery import Celery
from celery.utils.log import get_task_logger
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
logger = get_task_logger(__name__)

# Configure pool for Windows compatibility
celery_app.conf.update(worker_pool="solo" if os.name == "nt" else "prefork")

# Configure periodic scheduling (Celery Beat) if enabled via config.
if config.ANOMALY_SCHEDULE_ENABLED:
    celery_app.conf.beat_schedule = {
        "scan-all-assets-for-anomalies": {
            "task": "app.worker.scan_all_assets_for_anomalies",
            "schedule": config.ANOMALY_SCHEDULE_INTERVAL_SECONDS,
        }
    }
    logger.info(
        "[scheduler] beat_schedule enabled interval=%ds",
        config.ANOMALY_SCHEDULE_INTERVAL_SECONDS,
    )
else:
    logger.info("[scheduler] beat_schedule disabled")


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
            logger.info(
                "[anomaly] insufficient data asset=%s metric=%s count=%d window_seconds=%d",
                asset_id,
                metric,
                len(events),
                config.ANOMALY_WINDOW_SIZE_SECONDS,
            )
            return f"Not enough data points for {asset_id}/{metric} in the last window."

        values = np.array([event.value for event in events])
        mean = np.mean(values)
        std_dev = np.std(values)

        if std_dev == 0:  # Avoid division by zero
            logger.info(
                "[anomaly] zero std_dev asset=%s metric=%s mean=%.4f values=%d",
                asset_id,
                metric,
                mean,
                len(values),
            )
            return f"Standard deviation is zero for {asset_id}/{metric}."

        anomalies_detected = []
        logger.info(
            "[anomaly] evaluating asset=%s metric=%s count=%d mean=%.4f std=%.4f threshold=%.2f",
            asset_id,
            metric,
            len(values),
            mean,
            std_dev,
            config.ANOMALY_Z_SCORE_THRESHOLD,
        )
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
                logger.info(
                    "[anomaly] persisted asset=%s metric=%s telemetry_id=%s z=%.3f value=%.3f",
                    asset_id,
                    metric,
                    str(event.id),
                    abs(z_score),
                    event.value,
                )

        if anomalies_detected:
            msg = (
                f"Detected {len(anomalies_detected)} anomalies for {asset_id}/{metric}."
            )
            logger.info("[anomaly] summary %s", msg)
            return msg

        msg = f"No anomalies detected for {asset_id}/{metric}."
        logger.info("[anomaly] summary %s", msg)
        return msg

    finally:
        db.close()


@celery_app.task(name="app.worker.scan_all_assets_for_anomalies")
def scan_all_assets_for_anomalies():
    """
    Periodic task that enumerates distinct (asset_id, metric) pairs and enqueues
    anomaly detection tasks for each. Requires ANOMALY_SCHEDULE_ENABLED True and
    Celery Beat running. Uses ANOMALY_WINDOW_SIZE_SECONDS to limit scan to recent
    telemetry so we don't schedule stale metrics.
    """
    db: Session = SessionLocal()
    try:
        pairs = crud.get_distinct_asset_metric_pairs(
            db, window_seconds=config.ANOMALY_WINDOW_SIZE_SECONDS
        )
        if not pairs:
            logger.info(
                "[scheduler] no distinct asset/metric pairs found in recent window_seconds=%d",
                config.ANOMALY_WINDOW_SIZE_SECONDS,
            )
            return "No recent asset/metric pairs to scan."
        enqueued = 0
        for asset_id, metric in pairs:
            try:
                detect_anomalies.delay(asset_id, metric)
                enqueued += 1
            except Exception as ex:
                logger.warning(
                    "[scheduler] failed enqueue asset=%s metric=%s error=%s",
                    asset_id,
                    metric,
                    ex,
                )
        logger.info(
            "[scheduler] enqueued=%d pairs=%d window_seconds=%d",
            enqueued,
            len(pairs),
            config.ANOMALY_WINDOW_SIZE_SECONDS,
        )
        return f"Enqueued {enqueued} anomaly detection tasks from {len(pairs)} distinct pairs."
    finally:
        db.close()
