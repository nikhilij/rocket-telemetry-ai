# Scripts Directory

Utility scripts for development, testing, and analysis.

## 📁 Directory Structure

### Root Scripts

- **`cleanup.py`** - Clean up temporary and generated files
   - Removes Python artifacts (`__pycache__`, `*.pyc`)
   - Removes Celery/Redis files (`celerybeat-schedule*`, `dump.rdb`)
   - Removes temporary files (`.tmp_*`, `*.log`)
   - Removes IDE files (`.DS_Store`, `Thumbs.db`)

   ```bash
   python scripts/cleanup.py
   ```

### `analysis/`

Scripts for analyzing telemetry data and system health.

- **`check_data.py`** - Analyze telemetry data and anomaly detection status
   - Check data in the 10-minute detection window
   - Display statistical metrics (mean, std dev, Z-scores)
   - List all detected anomalies

   ```bash
   python scripts/analysis/check_data.py
   ```

- **`check_duplicates.py`** - Detect duplicate telemetry records
   - Find exact duplicates (same asset, metric, timestamp, value)
   - Detect timestamp collisions
   - Check recent data duplicates
   - Verify anomaly record uniqueness
   - Display duplication statistics

   ```bash
   python scripts/analysis/check_duplicates.py
   ```

### `data_generation/`

Scripts for generating test data with various scenarios.

- **`generate_test_data.py`** - Generate comprehensive test data
   - Multiple assets and metrics
   - Normal operation patterns
   - Stress test scenarios

   ```bash
   python scripts/data_generation/generate_test_data.py
   ```

- **`generate_current_test_data.py`** - Generate test data with current timestamps
   - Creates data with recent timestamps (within detection window)
   - Includes intentional anomalies for testing
   - Outputs to `current_test_with_anomalies.json`

   ```bash
   python scripts/data_generation/generate_current_test_data.py
   ```

### `testing/`

Scripts for testing API endpoints and system functionality.

- **`comprehensive_test.py`** - Complete API endpoint testing
   - Test /ingest endpoint
   - Test /ask endpoint with various queries
   - Test /summary endpoint
   - Test /metrics endpoint
   - Validate responses

   ```bash
   python scripts/testing/comprehensive_test.py
   ```

- **`test_imports.py`** - Verify all Python imports work correctly
   - Check application modules
   - Verify dependencies

   ```bash
   python scripts/testing/test_imports.py
   ```

- **`trigger_detection.py`** - Manually trigger anomaly detection
   - Force immediate anomaly detection run
   - Useful for testing without waiting for scheduled runs

   ```bash
   python scripts/testing/trigger_detection.py
   ```

## 🔧 Usage Tips

### Before Running Scripts

Make sure you're in the project root and have activated the virtual environment:

```bash
cd a:\Projects\rocket-telemetry-ai
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # Linux/Mac
```

### Common Workflows

**1. Generate and ingest fresh test data:**

```bash
# Generate data with current timestamps
python scripts/data_generation/generate_current_test_data.py

# Ingest the data
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d @current_test_with_anomalies.json

# Wait a few seconds for Celery to process
sleep 10

# Check the results
python scripts/analysis/check_data.py
```

**2. Validate data integrity:**

```bash
# Check for duplicates
python scripts/analysis/check_duplicates.py

# Analyze current data
python scripts/analysis/check_data.py
```

**3. Run comprehensive tests:**

```bash
# Test all API endpoints
python scripts/testing/comprehensive_test.py
```

## 📝 Notes

- All scripts assume the FastAPI server is running on `http://127.0.0.1:8000`
- Scripts in `analysis/` connect directly to the database
- Scripts in `testing/` use HTTP requests to API endpoints
- Generated test data files are created in the project root (unless specified otherwise)
