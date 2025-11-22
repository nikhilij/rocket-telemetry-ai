"""
Generate real-time telemetry data with current timestamps for testing anomaly detection.
This ensures the data falls within Celery's 10-minute detection window.
"""

import json
import requests
from datetime import datetime, timedelta
import random

BASE_URL = "http://localhost:8000"

def generate_realtime_telemetry_with_anomalies():
    """
    Generate telemetry data with current timestamps, including anomalous values.
    """
    now = datetime.utcnow()
    events = []
    
    # Define metrics with normal ranges and anomalous values
    metrics_config = {
        "engine_temp": {"normal": (600, 650), "anomaly": 850, "unit": "C"},
        "fuel_pressure": {"normal": (300, 350), "anomaly": 150, "unit": "PSI"},
        "altitude": {"normal": (1000, 2000), "anomaly": 50, "unit": "m"},
        "velocity": {"normal": (500, 600), "anomaly": 1200, "unit": "m/s"},
        "battery_voltage": {"normal": (24, 26), "anomaly": 15, "unit": "V"},
        "fuel_level": {"normal": (70, 90), "anomaly": 20, "unit": "%"},
        "acceleration_x": {"normal": (-2, 2), "anomaly": 25, "unit": "m/s^2"},
        "acceleration_y": {"normal": (-2, 2), "anomaly": -20, "unit": "m/s^2"},
        "acceleration_z": {"normal": (8, 12), "anomaly": 30, "unit": "m/s^2"},
        "gyroscope_x": {"normal": (-5, 5), "anomaly": 45, "unit": "deg/s"},
        "gyroscope_y": {"normal": (-5, 5), "anomaly": -40, "unit": "deg/s"},
        "gyroscope_z": {"normal": (-5, 5), "anomaly": 50, "unit": "deg/s"},
    }
    
    # Generate 30 data points over the last 9 minutes (within the 10-minute window)
    for i in range(30):
        timestamp = now - timedelta(seconds=540 - (i * 18))  # 18-second intervals
        
        for metric_name, config in metrics_config.items():
            # Most values are normal
            if i < 25:
                value = random.uniform(config["normal"][0], config["normal"][1])
            else:
                # Last 5 data points include anomalies for some metrics
                if metric_name in ["engine_temp", "fuel_pressure", "acceleration_z"]:
                    value = config["anomaly"]
                else:
                    value = random.uniform(config["normal"][0], config["normal"][1])
            
            event = {
                "asset_id": "rocket-1",
                "timestamp": timestamp.isoformat() + "Z",
                "metric": metric_name,
                "value": round(value, 2),
                "unit": config["unit"],
                "tags": {"test": "realtime_anomaly_detection"}
            }
            events.append(event)
    
    return events

def ingest_data(events):
    """Send events to the /ingest endpoint"""
    print(f"📊 Generating {len(events)} telemetry events with current timestamps...")
    print(f"⏰ Time range: Last 9 minutes (within 10-minute detection window)")
    print(f"🎯 Anomalies injected in: engine_temp, fuel_pressure, acceleration_z")
    
    response = requests.post(
        f"{BASE_URL}/ingest",
        json={"events": events},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Successfully ingested {result['ingested']} events")
        return True
    else:
        print(f"❌ Failed to ingest data: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

def check_metrics():
    """Check current system metrics"""
    response = requests.get(f"{BASE_URL}/metrics")
    if response.status_code == 200:
        data = response.json()
        print(f"\n📈 Current System Metrics:")
        print(f"   Total Events: {data['total_telemetry_events']}")
        print(f"   Total Anomalies: {data['total_anomaly_records']}")
        return data
    return None

def main():
    print("=" * 80)
    print("REAL-TIME ANOMALY DETECTION TEST")
    print("=" * 80)
    print("\n🎯 Purpose: Generate data with CURRENT timestamps to test Celery detection")
    print("⚠️  Celery detection window: Last 10 minutes (600 seconds)")
    print()
    
    # Generate and ingest data
    events = generate_realtime_telemetry_with_anomalies()
    
    if ingest_data(events):
        check_metrics()
        
        print("\n" + "=" * 80)
        print("NEXT STEPS")
        print("=" * 80)
        print("1. ✅ Data ingested with current timestamps")
        print("2. ⏳ Wait for Celery Beat to trigger detection (runs every 5 minutes)")
        print("3. 🔍 Watch the Celery worker terminal for detection logs")
        print("4. 📊 Run: python scripts/testing/verify_anomalies.py")
        print()
        print("💡 Expected: Celery should detect anomalies in:")
        print("   - engine_temp (value ~850°C, normal: 600-650°C)")
        print("   - fuel_pressure (value ~150 PSI, normal: 300-350 PSI)")
        print("   - acceleration_z (value ~30 m/s², normal: 8-12 m/s²)")
        print()
        print("🕐 Celery Beat schedule: Every 5 minutes")
        print("   Next detection will run in < 5 minutes")
    else:
        print("\n❌ Failed to ingest data. Check if FastAPI server is running.")

if __name__ == "__main__":
    main()
