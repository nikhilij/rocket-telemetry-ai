"""
Main FastAPI application.
"""

from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from . import crud, models, schemas, db

# Create all tables in the database.
# In a production app, you might want to use Alembic for migrations.
models.Base.metadata.create_all(bind=db.engine)

app = FastAPI(
    title="Telemetry Insight Agent Service",
    description="A backend service to ingest telemetry, detect anomalies, and provide AI-powered insights.",
    version="0.1.0",
)


@app.post("/ingest", response_model=schemas.TelemetryIngestResponse, status_code=200)
def ingest_telemetry(
    request: schemas.TelemetryIngestRequest, database: Session = Depends(db.get_db)
):
    """
    Accepts a batch of telemetry events.
    """
    try:
        # The spec allows for a single event or a batch.
        # This implementation standardizes on the batch format.
        if not request.events:
            return schemas.TelemetryIngestResponse(
                ingested=0, errors=["No events in request"]
            )

        events_to_create = [
            schemas.TelemetryEventCreate(raw_payload=event.dict(), **event.dict())
            for event in request.events
        ]

        num_ingested = crud.create_telemetry_events(
            db=database, events=events_to_create
        )
        return schemas.TelemetryIngestResponse(ingested=num_ingested)
    except Exception as e:
        # In a real app, log the exception details
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@app.get("/summary", response_model=schemas.SummaryResponse)
def get_summary(
    asset_id: str, window_minutes: int = 60, database: Session = Depends(db.get_db)
):
    """
    Runs RAG retrieval and returns an AI-generated health summary.
    """
    try:
        from . import agent

        return agent.get_summary_agent(asset_id, window_minutes)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate summary: {str(e)}"
        )


@app.post("/ask", response_model=schemas.AskResponse)
def ask_agent(request: schemas.AskRequest, database: Session = Depends(db.get_db)):
    """
    Natural language Q&A over telemetry data.
    """
    try:
        from . import agent

        return agent.get_qa_agent(request)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to answer question: {str(e)}"
        )


@app.get("/anomalies", response_model=List[schemas.AnomalyRecordInDB])
def get_anomalies(
    asset_id: str,
    since: datetime,
    until: Optional[datetime] = None,
    database: Session = Depends(db.get_db),
):
    """
    Returns anomaly records for an asset in a time range.
    """
    try:
        if until is None:
            until = datetime.utcnow()
        anomalies = crud.get_anomalies_by_asset(database, asset_id, since, until)
        return anomalies
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch anomalies: {str(e)}"
        )


@app.get("/metrics")
def get_metrics(database: Session = Depends(db.get_db)):
    """
    Exposes application metrics for monitoring.
    """
    try:
        from sqlalchemy import func
        from . import models

        # Get total telemetry events count
        total_events = database.query(func.count(models.TelemetryEvent.id)).scalar()

        # Get total anomaly records count
        total_anomalies = database.query(func.count(models.AnomalyRecord.id)).scalar()

        # Get events by asset (top 10)
        events_by_asset = (
            database.query(
                models.TelemetryEvent.asset_id,
                func.count(models.TelemetryEvent.id).label("count"),
            )
            .group_by(models.TelemetryEvent.asset_id)
            .order_by(func.count(models.TelemetryEvent.id).desc())
            .limit(10)
            .all()
        )

        # Get anomalies by asset (top 10)
        anomalies_by_asset = (
            database.query(
                models.AnomalyRecord.asset_id,
                func.count(models.AnomalyRecord.id).label("count"),
            )
            .group_by(models.AnomalyRecord.asset_id)
            .order_by(func.count(models.AnomalyRecord.id).desc())
            .limit(10)
            .all()
        )

        return {
            "total_telemetry_events": total_events,
            "total_anomaly_records": total_anomalies,
            "top_assets_by_events": [
                {"asset_id": a, "count": c} for a, c in events_by_asset
            ],
            "top_assets_by_anomalies": [
                {"asset_id": a, "count": c} for a, c in anomalies_by_asset
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch metrics: {str(e)}"
        )
