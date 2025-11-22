# Test Data Directory

Organized test data files for the Rocket Telemetry AI system.

## 📁 Directory Structure

```
tests/data/
├── anomalous/              # Test data with anomalies
│   ├── current_anomalies.json
│   ├── current_test_with_anomalies.json
│   ├── full_window_anomalous_test.json
│   ├── recent_anomalous_test.json
│   ├── test_data_anomalous_data.json
│   └── test_extreme_anomalies.json
├── normal/                 # Normal operation test data
│   ├── comprehensive_test_data.json
│   ├── sample_data.json
│   ├── test_data_launch_sequence.json
│   ├── test_data_multi_asset_normal.json
│   ├── test_data_normal_operation.json
│   └── test_data_stress_test_large.json
└── queries/                # Sample API queries
    ├── ask_request.json
    └── simple_ask.json
```

## 📋 Test Data Categories

### Anomalous Data (`anomalous/`)

Test data files containing intentional anomalies for testing detection capabilities.

- **`current_test_with_anomalies.json`** - Fresh data with current timestamps and extreme anomalies
   - Used for testing real-time anomaly detection
   - Contains anomalies in: engine_temp, fuel_pressure, fuel_level, altitude, velocity, acceleration

- **`test_data_anomalous_data.json`** - General anomalous data
   - Various anomaly patterns
   - Multiple metrics affected

- **`test_extreme_anomalies.json`** - Extreme edge cases
   - Very high Z-score anomalies
   - Stress testing detection threshold

- **`recent_anomalous_test.json`** - Recent data with anomalies
   - Within detection window
   - Quick testing

- **`full_window_anomalous_test.json`** - Full 10-minute window with anomalies
   - Tests entire detection window
   - Multiple time points

- **`current_anomalies.json`** - Currently detected anomalies
   - Output from anomaly detection
   - Reference data

### Normal Data (`normal/`)

Test data representing normal rocket operations without anomalies.

- **`sample_data.json`** - Basic sample data
   - Quick testing
   - 10-20 events
   - Single asset

- **`comprehensive_test_data.json`** - Comprehensive normal data
   - All metrics covered
   - Multiple assets
   - Good for general testing

- **`test_data_normal_operation.json`** - 30 minutes of normal operation
   - Realistic operational data
   - No anomalies
   - All metrics within normal ranges

- **`test_data_launch_sequence.json`** - Complete rocket launch sequence
   - Pre-launch, launch, flight, landing phases
   - Realistic metric progressions
   - Good for time-series testing

- **`test_data_multi_asset_normal.json`** - Multiple assets operating normally
   - 2+ rocket assets
   - Tests multi-asset handling
   - No anomalies

- **`test_data_stress_test_large.json`** - Large dataset for performance testing
   - 1000+ events
   - Tests ingestion performance
   - Tests query performance

### Query Examples (`queries/`)

Sample API request payloads for testing endpoints.

- **`ask_request.json`** - Sample /ask endpoint requests
   - Various question formats
   - Different query types

- **`simple_ask.json`** - Simple question examples
   - Minimal request format
   - Quick testing

## 🚀 Usage

### Ingesting Test Data

```bash
# Ingest normal operation data
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d @tests/data/normal/sample_data.json

# Ingest anomalous data
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d @tests/data/anomalous/current_test_with_anomalies.json
```

### Using Query Examples

```bash
# Use a query example
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d @tests/data/queries/simple_ask.json
```

## 🔧 Generating New Test Data

Use the data generation scripts to create fresh test data:

```bash
# Generate data with current timestamps
python scripts/data_generation/generate_current_test_data.py

# Generate comprehensive test data
python scripts/data_generation/generate_test_data.py
```

## 📝 Notes

- All timestamps in test data should be in ISO 8601 format
- Anomalous data files should have clear anomalies (Z-score > 2.0)
- Normal data should have realistic metric ranges
- Use current timestamps for testing real-time detection (10-minute window)

## Test Data Format

All test data files follow this JSON structure:

```json
{
   "events": [
      {
         "asset_id": "rocket-1",
         "timestamp": "2025-11-20T12:00:00Z",
         "metric": "engine_temp",
         "value": 2650.5,
         "unit": "C"
      }
   ]
}
```
