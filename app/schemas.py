"""
Pydantic schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

# --- Telemetry Schemas ---


class TelemetryEventBase(BaseModel):
    asset_id: str = Field(..., example="vehicle-1")
    timestamp: datetime = Field(..., example="2025-11-01T12:00:00Z")
    metric: str = Field(..., example="engine_temp")
    value: float = Field(..., example=650.5)
    unit: Optional[str] = Field(None, example="C")
    tags: Optional[Dict[str, Any]] = Field(None, example={"zone": "A"})


class TelemetryEventCreate(TelemetryEventBase):
    raw_payload: Dict[str, Any]


class TelemetryEventInDB(TelemetryEventBase):
    id: uuid.UUID
    raw_payload: Dict[str, Any]

    class Config:
        from_attributes = True


class TelemetryIngestRequest(BaseModel):
    events: List[TelemetryEventBase]


class TelemetryIngestResponse(BaseModel):
    ingested: int
    errors: List[str] = []


# --- Anomaly Schemas ---


class AnomalyRecordBase(BaseModel):
    asset_id: str
    timestamp: datetime
    metric: str
    score: float
    explanation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AnomalyRecordCreate(AnomalyRecordBase):
    telemetry_id: Optional[uuid.UUID] = None


class AnomalyRecordInDB(AnomalyRecordBase):
    id: uuid.UUID
    telemetry_id: Optional[uuid.UUID]

    class Config:
        from_attributes = True


# --- Agent/API Schemas ---


class SummaryResponse(BaseModel):
    asset_id: str
    summary: str


class AskRequest(BaseModel):
    asset_id: str
    question: str
    window_minutes: int = 10


class AskResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
