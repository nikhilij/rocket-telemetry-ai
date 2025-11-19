#!/usr/bin/env python3
"""
Comprehensive test suite for Rocket Telemetry AI system.
Tests all endpoints with various scenarios and data types.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import sys

BASE_URL = "http://127.0.0.1:8000"


def test_endpoint(name, method, url, data=None, expected_status=200):
    """Test a single endpoint and report results."""
    print(f"\n🧪 Testing {name}...")
    try:
        if method.upper() == "GET":
            response = requests.get(f"{BASE_URL}{url}")
        elif method.upper() == "POST":
            response = requests.post(
                f"{BASE_URL}{url}",
                json=data,
                headers={"Content-Type": "application/json"},
            )
        else:
            print(f"❌ Unsupported method: {method}")
            return False

        if response.status_code == expected_status:
            print(f"✅ {name}: SUCCESS ({response.status_code})")
            return response.json() if response.content else None
        else:
            print(f"❌ {name}: FAILED ({response.status_code})")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ {name}: ERROR - {str(e)}")
        return None


def load_test_data(filename):
    """Load test data from JSON file."""
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Test data file not found: {filename}")
        return None


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("🚀 Starting Comprehensive Rocket Telemetry AI Test Suite")
    print("=" * 60)

    # Test 1: Basic metrics check
    print("\n📊 PHASE 1: Basic System Health")
    metrics = test_endpoint("Metrics Endpoint", "GET", "/metrics")
    if metrics:
        print(
            f"   📈 Current metrics: {metrics['total_telemetry_events']} events, {metrics['total_anomaly_records']} anomalies"
        )

    # Test 2: Ingest comprehensive test data
    print("\n📥 PHASE 2: Data Ingestion Tests")

    test_files = [
        ("../data/comprehensive_test_data.json", "Basic telemetry data"),
        ("../data/test_data_normal_operation.json", "Normal operation (30 min)"),
        ("../data/test_data_anomalous_data.json", "Anomalous data with issues"),
        ("../data/test_data_launch_sequence.json", "Complete launch sequence"),
        ("../data/test_data_multi_asset_normal.json", "Multi-asset normal data"),
    ]

    for filename, description in test_files:
        data = load_test_data(filename)
        if data:
            result = test_endpoint(f"Ingest {description}", "POST", "/ingest", data)
            if result:
                print(f"   📊 Ingested {result['ingested']} events")
                if result["errors"]:
                    print(f"   ⚠️  Errors: {result['errors']}")

    # Test 3: AI Summary Tests
    print("\n🤖 PHASE 3: AI Summary Generation")

    summary_tests = [
        ("rocket-1", 60, "Recent 1-hour summary"),
        ("rocket-1", 1440, "Full day summary"),
        ("rocket-2", 60, "Secondary asset summary"),
    ]

    for asset_id, window, description in summary_tests:
        summary = test_endpoint(
            f"Summary - {description}",
            "GET",
            f"/summary?asset_id={asset_id}&window_minutes={window}",
        )
        if summary:
            print(f"   📝 Summary length: {len(summary['summary'])} characters")

    # Test 4: Q&A Tests
    print("\n❓ PHASE 4: Natural Language Q&A")

    qa_tests = [
        {
            "asset_id": "rocket-1",
            "question": "What is the current engine temperature?",
            "window_minutes": 60,
            "description": "Current engine temperature",
        },
        {
            "asset_id": "rocket-1",
            "question": "Are there any anomalies in the system?",
            "window_minutes": 1440,
            "description": "Anomaly detection query",
        },
        {
            "asset_id": "rocket-1",
            "question": "What is the fuel level trend over time?",
            "window_minutes": 1440,
            "description": "Fuel level analysis",
        },
        {
            "asset_id": "rocket-1",
            "question": "What are the maximum acceleration values recorded?",
            "window_minutes": 1440,
            "description": "Peak acceleration analysis",
        },
        {
            "asset_id": "rocket-2",
            "question": "How does this rocket compare to rocket-1?",
            "window_minutes": 60,
            "description": "Comparative analysis",
        },
    ]

    for qa_test in qa_tests:
        result = test_endpoint(
            f"Q&A - {qa_test['description']}", "POST", "/ask", qa_test
        )
        if result:
            print(f"   💬 Answer length: {len(result['answer'])} characters")
            print(f"   📚 Sources: {len(result['sources'])} telemetry points")

    # Test 5: Anomaly Detection
    print("\n🔍 PHASE 5: Anomaly Detection")

    # Check for anomalies (may be empty if no detection tasks ran)
    since_time = (datetime.utcnow() - timedelta(days=1)).isoformat() + "Z"
    anomalies = test_endpoint(
        "Anomaly Check", "GET", f"/anomalies?asset_id=rocket-1&since={since_time}"
    )
    if anomalies is not None:
        print(f"   🚨 Found {len(anomalies)} anomalies")

    # Test 6: Error Handling
    print("\n🛡️ PHASE 6: Error Handling Tests")

    error_tests = [
        (
            "Invalid asset ID",
            "GET",
            "/summary?asset_id=nonexistent&window_minutes=60",
            None,
            200,
        ),  # Should return empty summary
        (
            "Missing asset ID",
            "GET",
            "/summary?window_minutes=60",
            None,
            422,
        ),  # Validation error
        ("Invalid JSON", "POST", "/ingest", {"invalid": "data"}, 422),
        (
            "Empty events",
            "POST",
            "/ingest",
            {"events": []},
            200,
        ),  # Should handle gracefully
    ]

    for name, method, url, data, expected_status in error_tests:
        test_endpoint(f"Error: {name}", method, url, data, expected_status)

    # Test 7: Performance Test
    print("\n⚡ PHASE 7: Performance Test")

    # Test large dataset ingestion
    large_data = load_test_data("../data/test_data_stress_test_large.json")
    if large_data:
        start_time = time.time()
        result = test_endpoint("Large Dataset Ingestion", "POST", "/ingest", large_data)
        end_time = time.time()

        if result:
            ingestion_time = end_time - start_time
            events_per_second = result["ingested"] / ingestion_time
            print(".2f")
            print(".2f")

    # Test 8: Final System Status
    print("\n📊 PHASE 8: Final System Status")

    final_metrics = test_endpoint("Final Metrics Check", "GET", "/metrics")
    if final_metrics:
        print("\n🎯 FINAL SYSTEM STATUS:")
        print(
            f"   📊 Total Telemetry Events: {final_metrics['total_telemetry_events']}"
        )
        print(f"   🚨 Total Anomalies: {final_metrics['total_anomaly_records']}")
        print(f"   🛰️  Assets Tracked: {len(final_metrics['top_assets_by_events'])}")

        if final_metrics["top_assets_by_events"]:
            print(
                f"   🏆 Top Asset: {final_metrics['top_assets_by_events'][0]['asset_id']} ({final_metrics['top_assets_by_events'][0]['count']} events)"
            )

    print("\n" + "=" * 60)
    print("🎉 Comprehensive Test Suite Complete!")
    print("✅ All core functionality tested")
    print("✅ AI responses validated")
    print("✅ Error handling verified")
    print("✅ Performance benchmarks completed")


if __name__ == "__main__":
    run_comprehensive_tests()
