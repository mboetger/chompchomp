from celery import Celery
import os

# Set up Celery broker and backend URLs from environment variables, with defaults
broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
backend_url = os.getenv('CELERY_BACKEND_URL', 'redis://localhost:6379/0')

# Initialize Celery app with broker and backend URLs
app = Celery('tasks', broker=broker_url, backend=backend_url)
app.control.purge()
