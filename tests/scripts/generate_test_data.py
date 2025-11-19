#!/usr/bin/env python3
"""
Comprehensive test data generator for Rocket Telemetry AI system.
Generates realistic rocket telemetry data for testing.
"""

import json
import random
from datetime import datetime, timedelta
import numpy as np


def generate_normal_telemetry(
    asset_id: str, base_time: datetime, duration_minutes: int = 60
) -> list:
    """Generate normal rocket telemetry data."""
    events = []
    current_time = base_time

    while current_time < base_time + timedelta(minutes=duration_minutes):
        # Normal operating ranges
        telemetry_data = {
            "engine_temp": random.uniform(600, 750),  # Celsius
            "fuel_pressure": random.uniform(2400, 2600),  # psi
            "acceleration_x": random.uniform(-0.5, 0.5),  # m/s²
            "acceleration_y": random.uniform(-0.5, 0.5),  # m/s²
            "acceleration_z": random.uniform(9.5, 10.0),  # m/s² (gravity)
            "velocity": min(current_time.minute * 10, 800),  # m/s (increasing)
            "altitude": min(current_time.minute * 100, 5000),  # meters
            "fuel_level": max(100 - current_time.minute * 1.5, 10),  # %
            "battery_voltage": random.uniform(28.0, 29.0),  # V
            "gyroscope_x": random.uniform(-2, 2),  # deg/s
            "gyroscope_y": random.uniform(-2, 2),  # deg/s
            "gyroscope_z": random.uniform(-2, 2),  # deg/s
        }

        for metric, value in telemetry_data.items():
            unit = {
                "engine_temp": "C",
                "fuel_pressure": "psi",
                "acceleration_x": "m/s²",
                "acceleration_y": "m/s²",
                "acceleration_z": "m/s²",
                "velocity": "m/s",
                "altitude": "m",
                "fuel_level": "%",
                "battery_voltage": "V",
                "gyroscope_x": "deg/s",
                "gyroscope_y": "deg/s",
                "gyroscope_z": "deg/s",
            }[metric]

            events.append(
                {
                    "asset_id": asset_id,
                    "timestamp": current_time.isoformat() + "Z",
                    "metric": metric,
                    "value": round(value, 2),
                    "unit": unit,
                }
            )

        current_time += timedelta(seconds=30)  # Data every 30 seconds

    return events


def generate_anomalous_telemetry(asset_id: str, base_time: datetime) -> list:
    """Generate telemetry data with anomalies."""
    events = []

    # Normal data first
    normal_time = base_time
    for i in range(10):
        events.extend(generate_normal_telemetry(asset_id, normal_time, 1))
        normal_time += timedelta(minutes=1)

    # Add anomalies
    anomaly_time = normal_time

    # Engine overheating anomaly
    for i in range(5):
        events.append(
            {
                "asset_id": asset_id,
                "timestamp": (anomaly_time + timedelta(seconds=i * 30)).isoformat()
                + "Z",
                "metric": "engine_temp",
                "value": 950 + i * 20,  # Critical overheating
                "unit": "C",
            }
        )

    # Fuel pressure drop anomaly
    for i in range(5):
        events.append(
            {
                "asset_id": asset_id,
                "timestamp": (anomaly_time + timedelta(seconds=i * 30)).isoformat()
                + "Z",
                "metric": "fuel_pressure",
                "value": 1800 - i * 100,  # Pressure dropping dangerously
                "unit": "psi",
            }
        )

    # Gyroscope spike (stability issue)
    for i in range(3):
        events.append(
            {
                "asset_id": asset_id,
                "timestamp": (anomaly_time + timedelta(seconds=i * 30)).isoformat()
                + "Z",
                "metric": "gyroscope_z",
                "value": 45 + i * 15,  # Excessive rotation
                "unit": "deg/s",
            }
        )

    return events


def generate_launch_sequence(asset_id: str, launch_time: datetime) -> list:
    """Generate complete launch sequence telemetry."""
    events = []

    # Pre-launch (T-10 minutes to T-0)
    pre_launch_time = launch_time - timedelta(minutes=10)
    while pre_launch_time < launch_time:
        events.extend(generate_normal_telemetry(asset_id, pre_launch_time, 1))
        pre_launch_time += timedelta(minutes=1)

    # Launch phase (T+0 to T+5 minutes)
    launch_phase_time = launch_time
    for minute in range(6):
        current_time = launch_phase_time + timedelta(minutes=minute)

        # Increasing acceleration during launch
        accel_z = 9.81 + minute * 20  # Building thrust

        telemetry_data = {
            "engine_temp": 650 + minute * 50,
            "fuel_pressure": 2500 + minute * 100,
            "acceleration_x": random.uniform(-1, 1),
            "acceleration_y": random.uniform(-1, 1),
            "acceleration_z": accel_z,
            "velocity": minute * 200,  # Rapid acceleration
            "altitude": minute * 1200,  # Climbing fast
            "fuel_level": max(100 - minute * 15, 0),
            "battery_voltage": 28.5,
            "gyroscope_x": random.uniform(-5, 5),
            "gyroscope_y": random.uniform(-5, 5),
            "gyroscope_z": random.uniform(-5, 5),
        }

        for metric, value in telemetry_data.items():
            unit = {
                "engine_temp": "C",
                "fuel_pressure": "psi",
                "acceleration_x": "m/s²",
                "acceleration_y": "m/s²",
                "acceleration_z": "m/s²",
                "velocity": "m/s",
                "altitude": "m",
                "fuel_level": "%",
                "battery_voltage": "V",
                "gyroscope_x": "deg/s",
                "gyroscope_y": "deg/s",
                "gyroscope_z": "deg/s",
            }[metric]

            events.append(
                {
                    "asset_id": asset_id,
                    "timestamp": current_time.isoformat() + "Z",
                    "metric": metric,
                    "value": round(value, 2),
                    "unit": unit,
                }
            )

    return events


def main():
    """Generate comprehensive test datasets."""
    base_time = datetime(2025, 11, 20, 8, 0, 0)

    # Generate different test scenarios
    datasets = {
        "normal_operation.json": generate_normal_telemetry("rocket-1", base_time, 30),
        "anomalous_data.json": generate_anomalous_telemetry("rocket-1", base_time),
        "launch_sequence.json": generate_launch_sequence("rocket-1", base_time),
        "multi_asset_normal.json": (
            generate_normal_telemetry("rocket-1", base_time, 15)
            + generate_normal_telemetry("rocket-2", base_time, 15)
        ),
        "stress_test_large.json": generate_normal_telemetry(
            "rocket-1", base_time, 120
        ),  # 2 hours of data
    }

    for filename, events in datasets.items():
        data = {"events": events}
        with open(f"../data/test_data_{filename}", "w") as f:
            json.dump(data, f, indent=2)

        print(f"Generated {filename}: {len(events)} telemetry events")

    print("\nTest data generation complete!")
    print("Files created:")
    for filename in datasets.keys():
        print(f"  - test_data_{filename}")


if __name__ == "__main__":
    main()
