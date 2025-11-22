"""
Comprehensive endpoint testing script for Rocket Telemetry AI System
Tests all endpoints: /ingest, /ask, /summary, /metrics, /anomalies
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_DATA_DIR = Path(__file__).parent.parent.parent / "tests" / "data"

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_result(endpoint, status_code, response_data):
    """Print formatted test result"""
    status = "✅ PASS" if status_code == 200 else "❌ FAIL"
    print(f"\n{status} - {endpoint}")
    print(f"Status Code: {status_code}")
    if isinstance(response_data, dict):
        print(f"Response: {json.dumps(response_data, indent=2)}")
    else:
        print(f"Response: {response_data}")

def test_ingest_data(file_path):
    """Test /ingest endpoint"""
    print_header(f"TEST 1: INGEST DATA - {file_path.name}")
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print(f"📊 Loading {len(data)} telemetry events...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ingest",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        print_result("/ingest", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_metrics():
    """Test /metrics endpoint"""
    print_header("TEST 2: GET METRICS")
    
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        print_result("/metrics", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_anomalies(asset_id="rocket-1"):
    """Test /anomalies endpoint"""
    print_header(f"TEST 3: GET ANOMALIES - {asset_id}")
    
    try:
        # Get anomalies from last 24 hours
        from datetime import timedelta
        since = (datetime.now() - timedelta(hours=24)).isoformat()
        
        response = requests.get(
            f"{BASE_URL}/anomalies",
            params={
                "asset_id": asset_id,
                "since": since
            }
        )
        data = response.json()
        print_result(f"/anomalies?asset_id={asset_id}", response.status_code, data)
        
        if response.status_code == 200:
            print(f"\n📈 Found {len(data)} anomalies")
            if data:
                print("\nSample anomaly:")
                print(f"  Asset: {data[0].get('asset_id')}")
                print(f"  Metric: {data[0].get('metric_name')}")
                print(f"  Value: {data[0].get('value')}")
                print(f"  Z-score: {data[0].get('z_score')}")
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_summary(asset_id="rocket-1"):
    """Test /summary endpoint"""
    print_header(f"TEST 4: GET SUMMARY - {asset_id}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/summary",
            params={
                "asset_id": asset_id,
                "window_minutes": 60
            }
        )
        data = response.json()
        print_result(f"/summary?asset_id={asset_id}", response.status_code, data)
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ask_queries():
    """Test /ask endpoint with multiple queries"""
    print_header("TEST 5: NATURAL LANGUAGE QUERIES (/ask)")
    
    queries = [
        "Are there any anomalies?",
        "Show me fuel pressure data",
        "What is the status of rocket-1?",
        "Show recent temperature readings",
        "List all anomalies detected"
    ]
    
    results = []
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        try:
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": query},  # Fixed: use 'question' not 'query'
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print(f"Answer: {data.get('answer', 'No answer')[:200]}...")
            else:
                print(f"Error: {data}")
            results.append(response.status_code == 200)
        except Exception as e:
            print(f"❌ Error: {e}")
            results.append(False)
        
        time.sleep(2)  # Rate limiting for AI calls
    
    return all(results)

def test_health_check():
    """Test API availability"""
    print_header("TEST 0: API AVAILABILITY CHECK")
    
    try:
        # Test /metrics as a simple health check
        response = requests.get(f"{BASE_URL}/metrics")
        print(f"API Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ API is responding")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all endpoint tests"""
    print("\n" + "🚀"*40)
    print("  ROCKET TELEMETRY AI - COMPREHENSIVE ENDPOINT TESTING")
    print("🚀"*40)
    
    results = {}
    
    # Test 0: Health Check
    results['health'] = test_health_check()
    time.sleep(1)
    
    # Test 1: Ingest normal data
    normal_data_file = TEST_DATA_DIR / "normal" / "test_data_normal_operation.json"
    if normal_data_file.exists():
        results['ingest_normal'] = test_ingest_data(normal_data_file)
        time.sleep(2)
    else:
        print(f"⚠️  Normal data file not found: {normal_data_file}")
        results['ingest_normal'] = False
    
    # Test 1b: Ingest anomalous data
    anomalous_data_file = TEST_DATA_DIR / "anomalous" / "test_data_anomalous_data.json"
    if anomalous_data_file.exists():
        results['ingest_anomalous'] = test_ingest_data(anomalous_data_file)
        time.sleep(2)
    else:
        print(f"⚠️  Anomalous data file not found: {anomalous_data_file}")
        results['ingest_anomalous'] = False
    
    # Test 2: Get Metrics
    results['metrics'] = test_metrics()
    time.sleep(1)
    
    # Test 3: Get Anomalies
    results['anomalies'] = test_anomalies("rocket-1")
    time.sleep(1)
    
    # Test 4: Get Summary
    results['summary'] = test_summary("rocket-1")
    time.sleep(1)
    
    # Test 5: Ask Queries
    results['ask'] = test_ask_queries()
    
    # Print final summary
    print_header("TEST RESULTS SUMMARY")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print("\n📊 Test Results:")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n🎯 Overall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is working perfectly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Please check the logs above.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
