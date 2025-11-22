# 🚀 Rocket Telemetry AI System

An intelligent telemetry monitoring system for rocket assets using AI-powered anomaly detection and natural language querying.

![System Architecture](image.png)

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Development](#development)
- [Configuration](#configuration)

## ✨ Features

- **Real-time Telemetry Ingestion**: Fast batch ingestion of telemetry data (8,000+ events/sec)
- **Automated Anomaly Detection**: Z-score based statistical anomaly detection running every 5 minutes
- **Natural Language Queries**: Ask questions about telemetry data in plain English
- **AI-Powered Summaries**: Get intelligent health summaries of your rocket assets
- **Multi-Asset Support**: Monitor multiple rocket assets simultaneously
- **Comprehensive Metrics**: Track 12+ different telemetry metrics including:
   - Acceleration (x, y, z)
   - Gyroscope (x, y, z)
   - Engine temperature
   - Fuel pressure & level
   - Altitude & velocity
   - Battery voltage

## 📁 Project Structure

```
rocket-telemetry-ai/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI application & endpoints
│   ├── agent.py                  # LangChain AI agents
│   ├── config.py                 # Configuration settings
│   ├── crud.py                   # Database operations
│   ├── db.py                     # Database connection
│   ├── models.py                 # SQLAlchemy models
│   ├── prompts.py                # AI prompt templates
│   ├── schemas.py                # Pydantic schemas
│   └── worker.py                 # Celery background tasks
│
├── scripts/                      # Utility scripts
│   ├── analysis/                 # Data analysis tools
│   │   ├── check_data.py         # Telemetry data analysis
│   │   └── check_duplicates.py   # Duplicate detection
│   ├── data_generation/          # Test data generators
│   │   ├── generate_test_data.py
│   │   └── generate_current_test_data.py
│   └── testing/                  # Testing utilities
│       ├── comprehensive_test.py
│       ├── test_imports.py
│       └── trigger_detection.py
│
├── tests/                        # Test data
│   ├── data/
│   │   ├── anomalous/            # Test data with anomalies
│   │   ├── normal/               # Normal operation test data
│   │   └── queries/              # Sample query data
│   └── README.md
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd rocket-telemetry-ai
```

2. **Create virtual environment**

```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate     # Linux/Mac
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

```bash
# Copy .env.example to .env and configure:
DATABASE_URL=postgresql://user:password@localhost/rocket_telemetry
REDIS_URL=redis://localhost:6379/0
GOOGLE_API_KEY=your_gemini_api_key
```

5. **Run database migrations**

```bash
# Initialize database tables
python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

### Running the Application

You need to run **3 services** simultaneously:

**Terminal 1 - FastAPI Server:**

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Celery Worker:**

```bash
celery -A app.worker.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat Scheduler:**

```bash
python -m celery -A app.worker beat --loglevel=info
```

### Quick Test

```bash
# Ingest test data
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d @tests/data/normal/sample_data.json

# Ask a question
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Are there any anomalies?"}'

# Get metrics
curl http://127.0.0.1:8000/metrics
```

## 📊 API Usage

### API Endpoints

- `POST /ingest` - Ingest telemetry data
- `POST /ask` - Natural language queries
- `POST /summary` - Get AI health summary
- `GET /metrics` - System metrics
- `GET /anomalies` - Retrieve anomalies

### Natural Language Queries

The `/ask` endpoint accepts simple natural language questions:

```bash
# Basic anomaly check
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Are there any anomalies?"}'

# Time-specific query
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me anomalies from the last 2 hours"}'

# Specific metrics
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the current engine temperature?"}'
```

### Example Questions

- "Are there any anomalies detected?"
- "Show me anomalies from the last 2 hours"
- "What is the current status?"
- "How are the rockets performing?"
- "Show me fuel pressure readings"
- "Any issues I should know about?"

### Ingesting Data

```bash
# Ingest telemetry events
curl -X POST http://127.0.0.1:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "events": [
      {
        "asset_id": "rocket-1",
        "timestamp": "2025-11-22T10:00:00Z",
        "metric": "engine_temp",
        "value": 650.5,
        "unit": "C"
      }
    ]
  }'
```

### Getting Metrics

```bash
# System metrics
curl http://127.0.0.1:8000/metrics

# Get anomalies
curl http://127.0.0.1:8000/anomalies?asset_id=rocket-1&limit=10
```

## 🛠️ Development

### Cleanup

```bash
# Remove temporary and generated files
python scripts/cleanup.py
```

### Running Analysis Scripts

```bash
# Check telemetry data and anomalies
python scripts/analysis/check_data.py

# Check for duplicate data
python scripts/analysis/check_duplicates.py
```

### Generating Test Data

```bash
# Generate test data with current timestamps
python scripts/data_generation/generate_current_test_data.py
```

### Testing

```bash
# 1. Generate real-time test data (with current timestamps)
python scripts/testing/generate_realtime_data.py

# 2. Test all API endpoints
python scripts/testing/test_all_endpoints.py

# 3. Verify anomaly detection is working
python scripts/testing/verify_anomalies.py
```

## 🔧 Configuration

Key configuration options in `app/config.py`:

- `ANOMALY_Z_SCORE_THRESHOLD`: 2.0 (statistical threshold for anomaly detection)
- `ANOMALY_WINDOW_SIZE_SECONDS`: 600 (10 minutes detection window)
- Celery Beat schedule: Every 5 minutes for anomaly detection

### Runtime Files

The following files are automatically generated when services run (already in .gitignore):

- `celerybeat-schedule*` - Celery Beat scheduler state
- `dump.rdb` - Redis database snapshot
- These files are safe to delete when services are stopped

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

Built with:

- FastAPI
- LangChain
- Google Gemini AI
- PostgreSQL
- Celery & Redis
- SQLAlchemy
