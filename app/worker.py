# app/worker.py
from celery import Celery
import os

# Load the REDIS_URL from an environment variable, defaulting to localhost
# if not set (for local testing without Docker)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Initialize the Celery application
celery_app = Celery(
    "code_reviewer",        # This is the name of our task module
    broker=REDIS_URL,       # The connection URL for our broker (Redis)
    backend=REDIS_URL,      # The connection URL for our results backend (Redis)
    include=['app.celery_tasks']  # List of modules to import when the worker starts
)

# Optional configuration
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)