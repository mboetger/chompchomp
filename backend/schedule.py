import os
from celery import Celery
from celery.schedules import crontab

# Set up Celery broker and backend URLs from environment variables, with defaults
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend_url = os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')

# Initialize Celery app with broker and backend URLs
app = Celery('tasks', broker=broker_url, backend=backend_url)

# Schedule the workflow task to run every day at 2:00 AM
app.conf.beat_schedule = {
    'run-workflow-every-day': {
        'task': 'tasks.workflow',
        'schedule': crontab(hour='2,8,14,20', minute=20),
    },
}

app.conf.timezone = 'America/Los_Angeles'  # Set your timezone to PST