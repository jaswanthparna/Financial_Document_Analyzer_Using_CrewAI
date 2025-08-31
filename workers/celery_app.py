from celery import Celery
import os
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Celery app
celery_app = Celery(
    "financial_analyzer",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=['workers.tasks']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    result_expires=3600,  # 1 hour
)

def get_celery_app():
    """Get the configured Celery app instance."""
    return celery_app