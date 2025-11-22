#!/usr/bin/env python3
"""
Check telemetry data and anomaly detection status.

Usage:
    python scripts/analysis/check_data.py
"""

import sys
import os

# Add project root to path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../", "../"))
)

from app.db import SessionLocal
from app import models
from datetime import datetime, timedelta, timezone
import numpy as np

db = SessionLocal()

print("=" * 60)
print("TELEMETRY DATA ANALYSIS")
print("=" * 60)

# Check recent data in the detection window (10 minutes)
end = datetime.now(timezone.utc)
start = end - timedelta(minutes=10)

metrics_to_check = [
    "engine_temp",
    "fuel_pressure",
    "fuel_level",
    "altitude",
    "velocity",
    "acceleration_x",
]

print(f"\nData in last 10 minutes (detection window):")
print("-" * 60)

for metric in metrics_to_check:
    events = (
        db.query(models.TelemetryEvent)
        .filter(
            models.TelemetryEvent.metric == metric,
            models.TelemetryEvent.timestamp >= start,
            models.TelemetryEvent.timestamp <= end,
        )
        .all()
    )

    if events:
        values = [e.value for e in events]
        mean = np.mean(values)
        std = np.std(values)

        print(f"\n{metric}:")
        print(f"  Count: {len(values)}")
        print(f"  Range: {min(values):.2f} to {max(values):.2f}")
        print(f"  Mean: {mean:.2f}, Std Dev: {std:.2f}")

        # Check for potential anomalies (Z-score > 2.0)
        if std > 0:
            z_scores = [(v - mean) / std for v in values]
            anomalous = [i for i, z in enumerate(z_scores) if abs(z) > 2.0]
            if anomalous:
                print(f"  ⚠️  {len(anomalous)} values with Z-score > 2.0:")
                for idx in anomalous[:5]:  # Show first 5
                    print(
                        f"     Value: {values[idx]:.2f}, Z-score: {z_scores[idx]:.2f}"
                    )
    else:
        print(f"\n{metric}: No data in last 10 minutes")

print("\n" + "=" * 60)
print("ANOMALY RECORDS")
print("=" * 60)

anomalies = db.query(models.AnomalyRecord).all()
print(f"\nTotal anomalies detected: {len(anomalies)}")

for a in anomalies:
    print(f"\n  Asset: {a.asset_id}")
    print(f"  Metric: {a.metric}")
    print(f"  Time: {a.timestamp}")
    print(f"  Score: {a.score:.2f}")
    print(f"  Explanation: {a.explanation}")

print("\n" + "=" * 60)

db.close()
