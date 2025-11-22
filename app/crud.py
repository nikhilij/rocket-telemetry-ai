"""
CRUD (Create, Read, Update, Delete) operations for the database.
"""

from sqlalchemy.orm import Session
from . import models, schemas
from typing import List
from datetime import datetime


def create_telemetry_events(
    db: Session, events: List[schemas.TelemetryEventCreate]
) -> int:
    """
    Inserts a list of telemetry events into the database.
    """
    import json

    db_events = [
        models.TelemetryEvent(
            asset_id=event.asset_id,
            timestamp=event.timestamp,
            metric=event.metric,
            value=event.value,
            unit=event.unit,
            tags=event.tags,
            raw_payload=json.dumps(event.model_dump(mode="json")),
        )
        for event in events
    ]
    db.add_all(db_events)
    db.commit()
    # Return the number of events successfully added.
    # In a real app, you might return the actual objects or their IDs.
    return len(db_events)


def get_telemetry_events_by_metric(
    db: Session, asset_id: str, metric: str, start_time: datetime, end_time: datetime
) -> List[models.TelemetryEvent]:
    """
    Retrieves telemetry events for a specific metric and time window, ordered by time.
    """
    return (
        db.query(models.TelemetryEvent)
        .filter(
            models.TelemetryEvent.asset_id == asset_id,
            models.TelemetryEvent.metric == metric,
            models.TelemetryEvent.timestamp >= start_time,
            models.TelemetryEvent.timestamp <= end_time,
        )
        .order_by(models.TelemetryEvent.timestamp.asc())
        .all()
    )


def create_anomaly_record(
    db: Session, anomaly: schemas.AnomalyRecordCreate
) -> models.AnomalyRecord:
    """
    Creates a new anomaly record in the database.

    Dedup strategy: If an anomaly already exists for the same telemetry_id
    we return the existing record instead of inserting a duplicate. This
    prevents repeated anomaly rows when the detection window reprocesses
    unchanged outlier telemetry events.
    """
    if anomaly.telemetry_id:
        existing = (
            db.query(models.AnomalyRecord)
            .filter(models.AnomalyRecord.telemetry_id == anomaly.telemetry_id)
            .first()
        )
        if existing:
            return existing
    db_anomaly = models.AnomalyRecord(**anomaly.dict())
    db.add(db_anomaly)
    db.commit()
    db.refresh(db_anomaly)
    return db_anomaly


def get_anomalies_by_asset(
    db: Session, asset_id: str, start_time: datetime, end_time: datetime
) -> List[models.AnomalyRecord]:
    """
    Retrieves anomaly records for a specific asset and time window.
    """
    return (
        db.query(models.AnomalyRecord)
        .filter(
            models.AnomalyRecord.asset_id == asset_id,
            models.AnomalyRecord.timestamp >= start_time,
            models.AnomalyRecord.timestamp <= end_time,
        )
        .order_by(models.AnomalyRecord.timestamp.desc())
        .all()
    )


def get_telemetry_for_agent(
    db: Session, asset_id: str, start_time: datetime, end_time: datetime
) -> List[models.TelemetryEvent]:
    """
    Retrieves telemetry data for a given asset within a time window.
    This function is optimized for agent retrieval, potentially sampling data if needed.
    For now, it retrieves all data up to a limit to avoid overwhelming the LLM context.
    """
    return (
        db.query(models.TelemetryEvent)
        .filter(
            models.TelemetryEvent.asset_id == asset_id,
            models.TelemetryEvent.timestamp >= start_time,
            models.TelemetryEvent.timestamp <= end_time,
        )
        .order_by(models.TelemetryEvent.timestamp.desc())
        .limit(
            1000
        )  # Safeguard to prevent pulling too much data into the agent context
        .all()
    )
