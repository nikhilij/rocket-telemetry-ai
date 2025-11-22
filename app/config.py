"""
Centralized configuration settings for the application.
"""

import os
from dotenv import load_dotenv
from pydantic import SecretStr

load_dotenv()

# --- Database Configuration ---
POSTGRES_USER = os.getenv("POSTGRES_USER", "telemetry_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "kiit")
POSTGRES_DB = os.getenv("POSTGRES_DB", "telemetry_db")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")

DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{DATABASE_HOST}:{DATABASE_PORT}/{POSTGRES_DB}"
)

# --- Celery Configuration ---
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# --- Anomaly Detection Configuration ---
ANOMALY_Z_SCORE_THRESHOLD = float(os.getenv("ANOMALY_Z_SCORE_THRESHOLD", 3.0))
ANOMALY_WINDOW_SIZE_SECONDS = int(
    os.getenv("ANOMALY_WINDOW_SIZE_SECONDS", 600)
)  # 10 minutes


# Helper to parse boolean-like environment variables robustly.
def _parse_bool(value: str, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


# Toggle automatic enqueue of anomaly detection after ingestion.
AUTO_ENQUEUE_ANOMALY = _parse_bool(os.getenv("AUTO_ENQUEUE_ANOMALY"), True)

# Enable periodic scheduling of anomaly scans (Celery Beat required).
ANOMALY_SCHEDULE_ENABLED = _parse_bool(os.getenv("ANOMALY_SCHEDULE_ENABLED"), False)

# Interval (seconds) between scheduled anomaly scans when enabled.
ANOMALY_SCHEDULE_INTERVAL_SECONDS = int(
    os.getenv("ANOMALY_SCHEDULE_INTERVAL_SECONDS", 300)
)

# --- LangChain/Agent Configuration ---
# Google API Key for Gemini
_google_key = os.getenv("GOOGLE_API_KEY")
GOOGLE_API_KEY = SecretStr(_google_key) if _google_key else None

# LLM Provider (google_genai for Gemini)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "google_genai")

# Model name for Google Generative AI
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.5-flash")

# Summary window in minutes
SUMMARY_WINDOW_MINUTES = int(os.getenv("SUMMARY_WINDOW_MINUTES", 60))
