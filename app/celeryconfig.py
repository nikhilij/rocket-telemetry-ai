from celery.schedules import crontab

# Celery Beat schedule
beat_schedule = {
    'run-anomaly-detection-every-5-minutes': {
        'task': 'app.worker.run_anomaly_detection',
        'schedule': 300.0,  # Every 300 seconds (5 minutes)
    },
}