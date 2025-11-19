# Rocket Telemetry AI - Test Suite

This directory contains comprehensive tests and test data for the Rocket Telemetry AI system.

## Directory Structure

```
tests/
├── data/           # JSON test data files
│   ├── sample_data.json                    # Basic sample telemetry data
│   ├── comprehensive_test_data.json       # Basic test dataset
│   ├── test_data_normal_operation.json    # 30 minutes of normal operation
│   ├── test_data_anomalous_data.json      # Data with anomalies
│   ├── test_data_launch_sequence.json     # Complete rocket launch sequence
│   ├── test_data_multi_asset_normal.json  # Multi-asset normal data
│   └── test_data_stress_test_large.json   # Large dataset for performance testing
└── scripts/        # Python test scripts
    ├── comprehensive_test.py              # Full system test suite
    ├── generate_test_data.py              # Test data generator
    └── test_imports.py                    # Import validation tests
```

## Running Tests

### Comprehensive Test Suite

```bash
cd tests/scripts
python comprehensive_test.py
```

This will test all system endpoints with various scenarios including:

- Data ingestion
- AI summary generation
- Natural language Q&A
- Anomaly detection
- Error handling
- Performance benchmarks

### Generate Test Data

```bash
cd tests/scripts
python generate_test_data.py
```

This will regenerate all test data files in the `data/` directory.

### Individual Test Files

- `sample_data.json`: Basic telemetry data for quick testing
- `comprehensive_test_data.json`: Small dataset for basic functionality tests
- `test_data_normal_operation.json`: 30 minutes of normal rocket operation
- `test_data_anomalous_data.json`: Data containing various anomalies
- `test_data_launch_sequence.json`: Complete rocket launch sequence data
- `test_data_multi_asset_normal.json`: Normal data for multiple rocket assets
- `test_data_stress_test_large.json`: Large dataset (2880 events) for performance testing

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

## Notes

- All test scripts expect the FastAPI server to be running on `http://127.0.0.1:8000`
- Test data timestamps are generated relative to script execution time
- Anomaly detection tests require the Celery worker to be running
- Performance tests measure ingestion speed and system responsiveness
