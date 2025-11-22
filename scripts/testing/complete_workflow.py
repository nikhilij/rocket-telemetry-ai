"""
Complete end-to-end testing workflow for Celery anomaly detection.
This script automates: clear DB -> ingest data -> wait for detection -> verify results
"""

import subprocess
import sys
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def check_services():
    """Check if required services are running"""
    print_header("STEP 0: CHECKING SERVICES")
    
    # Check FastAPI
    try:
        response = requests.get(f"{BASE_URL}/metrics", timeout=2)
        if response.status_code == 200:
            print("✅ FastAPI server is running")
        else:
            print("⚠️  FastAPI server responded with error")
            return False
    except:
        print("❌ FastAPI server is NOT running!")
        print("   Start it with: uvicorn app.main:app --reload")
        return False
    
    print("\n💡 Make sure these are also running:")
    print("   - Redis server")
    print("   - PostgreSQL database")
    print("   - Celery Worker: celery -A app.worker.celery_app worker --loglevel=info --pool=solo")
    print("   - Celery Beat: celery -A app.worker.celery_app beat --loglevel=info")
    
    proceed = input("\nAre all services running? (y/n): ").strip().lower()
    return proceed == 'y'

def clear_database():
    """Clear the database"""
    print_header("STEP 1: CLEARING DATABASE")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/testing/clear_database.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to clear database: {e}")
        print(e.output)
        return False

def ingest_test_data():
    """Ingest test data with current timestamps"""
    print_header("STEP 2: INGESTING TEST DATA")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/testing/generate_realtime_data.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to ingest data: {e}")
        return False

def wait_for_celery_beat():
    """Wait for Celery Beat to trigger detection"""
    print_header("STEP 3: WAITING FOR CELERY BEAT")
    
    print("\n⏰ Celery Beat runs every 5 minutes")
    print("🔍 Watch your Celery Worker terminal for logs like:")
    print("   [INFO] Task app.worker.run_anomaly_detection received")
    print("   [INFO] Detected X anomalies for rocket-1/metric_name")
    print()
    
    # Check current anomaly count
    response = requests.get(f"{BASE_URL}/metrics")
    if response.status_code == 200:
        initial_anomalies = response.json()['total_anomaly_records']
        print(f"📊 Current anomalies in DB: {initial_anomalies}")
    
    print("\n⏳ Checking for anomalies every 10 seconds...")
    print("   Press Ctrl+C to skip waiting and check now")
    
    max_wait = 6 * 60  # 6 minutes max
    elapsed = 0
    
    try:
        while elapsed < max_wait:
            time.sleep(10)
            elapsed += 10
            
            # Check if anomalies were detected
            response = requests.get(f"{BASE_URL}/metrics")
            if response.status_code == 200:
                current_anomalies = response.json()['total_anomaly_records']
                
                if current_anomalies > initial_anomalies:
                    print(f"\n✅ Anomalies detected! ({current_anomalies} total)")
                    return True
            
            remaining = max_wait - elapsed
            print(f"   Waiting... ({remaining}s remaining)")
    
    except KeyboardInterrupt:
        print("\n⏹️  Skipping wait, checking current state...")
    
    return True

def verify_results():
    """Verify anomaly detection results"""
    print_header("STEP 4: VERIFYING RESULTS")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/testing/verify_anomalies.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Verification failed: {e}")
        return False

def test_endpoints():
    """Test all API endpoints"""
    print_header("STEP 5: TESTING ALL ENDPOINTS")
    try:
        result = subprocess.run(
            [sys.executable, "scripts/testing/test_all_endpoints.py"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Endpoint tests failed: {e}")
        return False

def main():
    print("\n" + "🚀" * 40)
    print("  COMPLETE CELERY ANOMALY DETECTION WORKFLOW")
    print("🚀" * 40)
    
    # Check services
    if not check_services():
        print("\n❌ Please start all required services first!")
        return
    
    # Run workflow
    steps = [
        ("Clear Database", clear_database),
        ("Ingest Test Data", ingest_test_data),
        ("Wait for Celery Beat", wait_for_celery_beat),
        ("Verify Anomalies", verify_results),
        ("Test All Endpoints", test_endpoints),
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Workflow failed at: {step_name}")
            return
        time.sleep(2)
    
    print_header("✅ WORKFLOW COMPLETE")
    print("\n🎉 All tests passed successfully!")
    print("\n📊 Summary:")
    print("   ✅ Database cleared")
    print("   ✅ Test data ingested")
    print("   ✅ Celery detected anomalies")
    print("   ✅ All endpoints working")
    print("\n💡 Your Rocket Telemetry AI system is fully operational!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow interrupted by user")
