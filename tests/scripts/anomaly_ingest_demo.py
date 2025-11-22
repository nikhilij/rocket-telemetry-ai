#!/usr/bin/env python3
"""Quick ingestion script to trigger anomaly detection.
Generates 11 recent telemetry events for a single asset/metric with one outlier
so the z-score exceeds the anomaly threshold (>3). Then queries anomalies.

Requirements: standard library only.
"""
import json
import time
from datetime import datetime, timezone, timedelta
from http.client import HTTPConnection

BASE_HOST = "127.0.0.1"
BASE_PORT = 8000
ASSET_ID = "rocket-1"
METRIC = "engine_temp"
UNIT = "C"

# We create 10 baseline values and 1 outlier.
# For m baseline identical values (m>=10) and one outlier, z-score = sqrt(m) > 3
# when m >= 10, so anomaly should be detected.
BASE_VALUE = 100.0
OUTLIER_VALUE = 300.0
BASE_COUNT = 10  # must be >=10 to exceed z-score threshold 3


def iso_now(offset_seconds: int = 0) -> str:
    return (
        (datetime.now(timezone.utc) - timedelta(seconds=offset_seconds))
        .isoformat()
        .replace("+00:00", "Z")
    )


def build_events():
    events = []
    # Spread baseline events over last 20 seconds.
    for i in range(BASE_COUNT):
        events.append(
            {
                "asset_id": ASSET_ID,
                "timestamp": iso_now(20 - i),
                "metric": METRIC,
                "value": BASE_VALUE,
                "unit": UNIT,
            }
        )
    # Add outlier at current timestamp
    events.append(
        {
            "asset_id": ASSET_ID,
            "timestamp": iso_now(0),
            "metric": METRIC,
            "value": OUTLIER_VALUE,
            "unit": UNIT,
        }
    )
    return events


def post_ingest(events):
    conn = HTTPConnection(BASE_HOST, BASE_PORT, timeout=10)
    payload = json.dumps({"events": events})
    headers = {"Content-Type": "application/json"}
    conn.request("POST", "/ingest", body=payload, headers=headers)
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    return resp.status, body


def get_anomalies(since_iso: str):
    conn = HTTPConnection(BASE_HOST, BASE_PORT, timeout=10)
    path = f"/anomalies?asset_id={ASSET_ID}&since={since_iso}"
    conn.request("GET", path)
    resp = conn.getresponse()
    body = resp.read().decode()
    conn.close()
    return resp.status, body


def main():
    events = build_events()
    print(f"Ingesting {len(events)} events (with one outlier)...")
    status, body = post_ingest(events)
    print(f"/ingest status={status} body={body}")

    # Allow Celery worker a moment to process anomaly task
    print("Waiting for anomaly detection task to run...")
    time.sleep(3)

    # Query anomalies from 5 minutes ago
    since = iso_now(300)
    a_status, a_body = get_anomalies(since)
    print(f"/anomalies status={a_status} body={a_body}")


if __name__ == "__main__":
    main()
