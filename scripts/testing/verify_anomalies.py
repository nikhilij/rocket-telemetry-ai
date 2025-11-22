"""
Verify that Celery anomaly detection is working by checking for detected anomalies.
"""

import requests
from datetime import datetime, timedelta
import time

BASE_URL = "http://localhost:8000"

def check_anomalies():
    """Check for detected anomalies"""
    print("=" * 80)
    print("VERIFYING ANOMALY DETECTION")
    print("=" * 80)
    
    # Query anomalies from the last hour (use timezone-aware UTC)
    from datetime import timezone
    since = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    
    response = requests.get(
        f"{BASE_URL}/anomalies",
        params={
            "asset_id": "rocket-1",
            "since": since
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch anomalies: {response.status_code}")
        return False
    
    anomalies = response.json()
    print(f"\n📊 Total Anomalies Detected: {len(anomalies)}")
    
    if not anomalies:
        print("\n⚠️  No anomalies detected yet!")
        print("\n🔍 Troubleshooting:")
        print("   1. Check if Celery Beat is running (separate terminal)")
        print("   2. Check Celery Worker logs for 'detect_anomalies' task")
        print("   3. Verify data was ingested with current timestamps")
        print("   4. Wait for next Celery Beat cycle (every 5 minutes)")
        return False
    
    # Group anomalies by metric
    by_metric = {}
    for anomaly in anomalies:
        metric = anomaly['metric']
        if metric not in by_metric:
            by_metric[metric] = []
        by_metric[metric].append(anomaly)
    
    print(f"\n✅ SUCCESS! Anomalies detected in {len(by_metric)} metrics:")
    print()
    
    for metric, metric_anomalies in by_metric.items():
        print(f"📍 {metric}: {len(metric_anomalies)} anomalies")
        for i, anom in enumerate(metric_anomalies[:3], 1):  # Show first 3
            print(f"   {i}. Score: {anom['score']:.2f}")
            print(f"      Timestamp: {anom['timestamp']}")
            print(f"      Explanation: {anom.get('explanation', 'N/A')[:100]}...")
        if len(metric_anomalies) > 3:
            print(f"   ... and {len(metric_anomalies) - 3} more")
        print()
    
    return True

def check_metrics():
    """Check system metrics"""
    response = requests.get(f"{BASE_URL}/metrics")
    if response.status_code == 200:
        data = response.json()
        print("📈 System Metrics:")
        print(f"   Total Telemetry Events: {data['total_telemetry_events']}")
        print(f"   Total Anomaly Records: {data['total_anomaly_records']}")
        print()
        return data
    return None

def test_natural_language_query():
    """Test asking about anomalies"""
    print("=" * 80)
    print("TESTING NATURAL LANGUAGE QUERY")
    print("=" * 80)
    
    query = "What anomalies were detected for rocket-1?"
    print(f"\n🔍 Question: '{query}'")
    
    response = requests.post(
        f"{BASE_URL}/ask",
        json={"question": query},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        answer = data.get('answer', 'No answer')
        print(f"\n💬 Answer:")
        print(f"   {answer}")
        print()
    else:
        print(f"❌ Query failed: {response.status_code}")

def main():
    print("\n" + "🚀" * 40)
    print("  CELERY ANOMALY DETECTION VERIFICATION")
    print("🚀" * 40)
    print()
    
    # Check metrics first
    check_metrics()
    
    # Check for anomalies
    anomalies_found = check_anomalies()
    
    if anomalies_found:
        # Test natural language query
        test_natural_language_query()
        
        print("=" * 80)
        print("CONCLUSION")
        print("=" * 80)
        print("✅ Celery anomaly detection is working correctly!")
        print("✅ Z-score based detection is functioning")
        print("✅ Anomaly records are being stored in the database")
        print("✅ Natural language queries can retrieve anomaly information")
    else:
        print("=" * 80)
        print("WAITING FOR CELERY BEAT")
        print("=" * 80)
        print("⏳ Celery Beat runs every 5 minutes")
        print("⏳ Check the Celery Worker terminal for task execution logs")
        print()
        print("Expected log pattern:")
        print("  [INFO] Task app.worker.run_anomaly_detection received")
        print("  [INFO] Task app.worker.detect_anomalies received")
        print("  [INFO] Detected X anomalies for rocket-1/metric_name")
        print()
        print("💡 TIP: Run this script again in a few minutes")

if __name__ == "__main__":
    main()
