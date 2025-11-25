"""
Celery application for async task processing.
"""
from celery import Celery
from celery.schedules import crontab

from utils.config import settings

# Create Celery app
celery_app = Celery(
    "smart_website_builder",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=settings.AGENT_TIMEOUT_SECONDS,
    task_soft_time_limit=settings.AGENT_TIMEOUT_SECONDS - 10,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

# Configure periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-old-sessions-daily": {
        "task": "services.tasks.cleanup_old_sessions",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM UTC
    },
    "cleanup-old-logs-daily": {
        "task": "services.tasks.cleanup_old_logs",
        "schedule": crontab(hour=3, minute=0),  # Run daily at 3 AM UTC
    },
    "cleanup-old-workflows-hourly": {
        "task": "services.tasks.cleanup_old_workflows",
        "schedule": crontab(minute=0),  # Run every hour
    },
}

# Auto-discover tasks
celery_app.autodiscover_tasks(["services.tasks"])
