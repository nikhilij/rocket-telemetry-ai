#!/usr/bin/env python3
"""
Generate test data with current timestamps and extreme anomalies across multiple metrics.

Usage:
    python scripts/data_generation/generate_current_test_data.py
"""

import json
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)

events = []

# Generate data for rocket-1 with multiple anomalies
for i in range(15):
    timestamp = (now - timedelta(minutes=14 - i)).isoformat()

    # Normal engine_temp data
    engine_temp = 500.0 + i * 5
    # Add extreme anomaly at minute 8
    if i == 8:
        engine_temp = 2000.0  # Extreme spike

    # Normal fuel_pressure
    fuel_pressure = 2500.0 + i * 10
    # Add anomaly at minute 10
    if i == 10:
        fuel_pressure = 5000.0  # Extreme spike

    # Normal fuel_level (should decrease)
    fuel_level = 100.0 - i * 2
    # Add anomaly at minute 12 (sudden drop)
    if i == 12:
        fuel_level = 10.0  # Critical low

    # Normal altitude
    altitude = i * 50.0
    # Add anomaly at minute 7
    if i == 7:
        altitude = 5000.0  # Sudden jump

    # Normal velocity
    velocity = i * 10.0
    # Add anomaly at minute 9
    if i == 9:
        velocity = 500.0  # Too fast

    # Normal acceleration
    accel_x = 0.1 * i
    accel_y = 0.1 * i
    accel_z = 9.81 + 0.5 * i

    # Add acceleration anomaly at minute 11
    if i == 11:
        accel_x = 100.0  # Extreme acceleration
        accel_z = 50.0

    events.extend(
        [
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "engine_temp",
                "value": engine_temp,
                "unit": "C",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "fuel_pressure",
                "value": fuel_pressure,
                "unit": "psi",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "fuel_level",
                "value": fuel_level,
                "unit": "%",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "altitude",
                "value": altitude,
                "unit": "m",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "velocity",
                "value": velocity,
                "unit": "m/s",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "acceleration_x",
                "value": accel_x,
                "unit": "m/s²",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "acceleration_y",
                "value": accel_y,
                "unit": "m/s²",
            },
            {
                "asset_id": "rocket-1",
                "timestamp": timestamp,
                "metric": "acceleration_z",
                "value": accel_z,
                "unit": "m/s²",
            },
        ]
    )

output = {"events": events}

with open("tests/data/current_test_with_anomalies.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"✅ Generated {len(events)} events with multiple anomalies")
print(f"   Expected anomalies in:")
print(f"   - engine_temp (minute 8): 2000.0°C")
print(f"   - fuel_pressure (minute 10): 5000.0 psi")
print(f"   - fuel_level (minute 12): 10.0%")
print(f"   - altitude (minute 7): 5000.0 m")
print(f"   - velocity (minute 9): 500.0 m/s")
print(f"   - acceleration_x (minute 11): 100.0 m/s²")
print(f"   - acceleration_z (minute 11): 50.0 m/s²")
