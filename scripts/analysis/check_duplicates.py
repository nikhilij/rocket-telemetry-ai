#!/usr/bin/env python3
"""
Check for duplicate telemetry data in the database.

Usage:
    python scripts/analysis/check_duplicates.py
"""

import sys
import os

# Add project root to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../", "../"))
)

from app.db import SessionLocal
from app import models
from sqlalchemy import func
from datetime import datetime, timedelta, timezone

db = SessionLocal()

print("=" * 80)
print("DUPLICATE DATA ANALYSIS")
print("=" * 80)

# Check 1: Exact duplicates (same asset_id, metric, timestamp, value)
print("\n1. EXACT DUPLICATES (same asset_id, metric, timestamp, value):")
print("-" * 80)

exact_duplicates = (
    db.query(
        models.TelemetryEvent.asset_id,
        models.TelemetryEvent.metric,
        models.TelemetryEvent.timestamp,
        models.TelemetryEvent.value,
        func.count(models.TelemetryEvent.id).label("count"),
    )
    .group_by(
        models.TelemetryEvent.asset_id,
        models.TelemetryEvent.metric,
        models.TelemetryEvent.timestamp,
        models.TelemetryEvent.value,
    )
    .having(func.count(models.TelemetryEvent.id) > 1)
    .all()
)

if exact_duplicates:
    print(f"Found {len(exact_duplicates)} sets of exact duplicates:")
    for dup in exact_duplicates[:10]:  # Show first 10
        print(f"\n  Asset: {dup.asset_id}")
        print(f"  Metric: {dup.metric}")
        print(f"  Timestamp: {dup.timestamp}")
        print(f"  Value: {dup.value}")
        print(f"  Count: {dup.count} duplicates")
else:
    print("✅ No exact duplicates found")

# Check 2: Same asset_id + metric + timestamp (but possibly different values)
print("\n\n2. SAME ASSET + METRIC + TIMESTAMP (potentially different values):")
print("-" * 80)

timestamp_duplicates = (
    db.query(
        models.TelemetryEvent.asset_id,
        models.TelemetryEvent.metric,
        models.TelemetryEvent.timestamp,
        func.count(models.TelemetryEvent.id).label("count"),
        func.array_agg(models.TelemetryEvent.value).label("values"),
    )
    .group_by(
        models.TelemetryEvent.asset_id,
        models.TelemetryEvent.metric,
        models.TelemetryEvent.timestamp,
    )
    .having(func.count(models.TelemetryEvent.id) > 1)
    .all()
)

if timestamp_duplicates:
    print(f"Found {len(timestamp_duplicates)} timestamp collisions:")
    for dup in timestamp_duplicates[:10]:  # Show first 10
        values_unique = set(dup.values) if dup.values else set()
        print(f"\n  Asset: {dup.asset_id}")
        print(f"  Metric: {dup.metric}")
        print(f"  Timestamp: {dup.timestamp}")
        print(f"  Count: {dup.count} records")
        print(f"  Values: {list(values_unique)}")
        if len(values_unique) == 1:
            print(f"  ⚠️  All values are identical - TRUE DUPLICATE")
        else:
            print(f"  ℹ️  Different values - timestamp collision")
else:
    print("✅ No timestamp collisions found")

# Check 3: Recent data (last 10 minutes) duplicates
print("\n\n3. RECENT DATA DUPLICATES (last 10 minutes):")
print("-" * 80)

end = datetime.now(timezone.utc)
start = end - timedelta(minutes=10)

recent_duplicates = (
    db.query(
        models.TelemetryEvent.asset_id,
        models.TelemetryEvent.metric,
        models.TelemetryEvent.timestamp,
        models.TelemetryEvent.value,
        func.count(models.TelemetryEvent.id).label("count"),
    )
    .filter(
        models.TelemetryEvent.timestamp >= start,
        models.TelemetryEvent.timestamp <= end,
    )
    .group_by(
        models.TelemetryEvent.asset_id,
        models.TelemetryEvent.metric,
        models.TelemetryEvent.timestamp,
        models.TelemetryEvent.value,
    )
    .having(func.count(models.TelemetryEvent.id) > 1)
    .all()
)

if recent_duplicates:
    print(f"Found {len(recent_duplicates)} duplicates in last 10 minutes:")
    for dup in recent_duplicates:
        print(f"\n  Asset: {dup.asset_id}")
        print(f"  Metric: {dup.metric}")
        print(f"  Timestamp: {dup.timestamp}")
        print(f"  Value: {dup.value}")
        print(f"  Count: {dup.count} duplicates")
else:
    print("✅ No duplicates in last 10 minutes")

# Check 4: Anomaly record duplicates
print("\n\n4. ANOMALY RECORD DUPLICATES:")
print("-" * 80)

anomaly_duplicates = (
    db.query(
        models.AnomalyRecord.asset_id,
        models.AnomalyRecord.metric,
        models.AnomalyRecord.timestamp,
        func.count(models.AnomalyRecord.id).label("count"),
    )
    .group_by(
        models.AnomalyRecord.asset_id,
        models.AnomalyRecord.metric,
        models.AnomalyRecord.timestamp,
    )
    .having(func.count(models.AnomalyRecord.id) > 1)
    .all()
)

if anomaly_duplicates:
    print(f"Found {len(anomaly_duplicates)} duplicate anomaly records:")
    for dup in anomaly_duplicates:
        print(f"\n  Asset: {dup.asset_id}")
        print(f"  Metric: {dup.metric}")
        print(f"  Timestamp: {dup.timestamp}")
        print(f"  Count: {dup.count} duplicates")
else:
    print("✅ No duplicate anomaly records")

# Summary statistics
print("\n\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

total_telemetry = db.query(func.count(models.TelemetryEvent.id)).scalar()
total_anomalies = db.query(func.count(models.AnomalyRecord.id)).scalar()

unique_telemetry = db.query(
    func.count(
        func.distinct(
            func.concat(
                models.TelemetryEvent.asset_id,
                models.TelemetryEvent.metric,
                models.TelemetryEvent.timestamp,
                models.TelemetryEvent.value,
            )
        )
    )
).scalar()

unique_anomalies = db.query(
    func.count(
        func.distinct(
            func.concat(
                models.AnomalyRecord.asset_id,
                models.AnomalyRecord.metric,
                models.AnomalyRecord.timestamp,
            )
        )
    )
).scalar()

print(f"\nTelemetry Events:")
print(f"  Total records: {total_telemetry}")
print(f"  Unique combinations: {unique_telemetry}")
print(f"  Duplicates: {total_telemetry - unique_telemetry}")
if total_telemetry > 0:
    print(
        f"  Duplication rate: {((total_telemetry - unique_telemetry) / total_telemetry * 100):.2f}%"
    )

print(f"\nAnomaly Records:")
print(f"  Total records: {total_anomalies}")
print(f"  Unique combinations: {unique_anomalies}")
print(f"  Duplicates: {total_anomalies - unique_anomalies}")
if total_anomalies > 0:
    print(
        f"  Duplication rate: {((total_anomalies - unique_anomalies) / total_anomalies * 100):.2f}%"
    )

print("\n" + "=" * 80)

db.close()
