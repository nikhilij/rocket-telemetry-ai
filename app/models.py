"""
SQLAlchemy models for the database tables.
"""

import uuid
from sqlalchemy import (
    Column,
    String,
    TIMESTAMP,
    Float,
    Text,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TelemetryEvent(Base):
    __tablename__ = "telemetry_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    asset_id = Column(String, nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    metric = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String)
    tags = Column(JSONB)
    raw_payload = Column(JSONB)


class AnomalyRecord(Base):
    __tablename__ = "anomaly_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    telemetry_id = Column(UUID(as_uuid=True), ForeignKey("telemetry_events.id"))
    asset_id = Column(String, nullable=False, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    metric = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    explanation = Column(Text)
    details = Column(JSONB)
