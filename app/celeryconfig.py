from celery.schedules import crontab

# Celery Beat schedule
beat_schedule = {
    'run-anomaly-detection-every-30-seconds': {
        'task': 'app.worker.run_anomaly_detection',
        'schedule': 30.0,  # Every 30 seconds
    },
}