from celery import Celery
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "ugc_saas_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        'app.tasks.metrics_tasks',
        'app.tasks.report_tasks',
        'app.tasks.ai_tasks',
        'app.tasks.email_tasks'
    ]
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
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks configuration
celery_app.conf.beat_schedule = {
    'collect-metrics-hourly': {
        'task': 'app.tasks.metrics_tasks.collect_all_metrics',
        'schedule': 3600.0,  # Every hour
    },
    'generate-weekly-reports': {
        'task': 'app.tasks.report_tasks.generate_weekly_reports',
        'schedule': 604800.0,  # Every week (Sunday)
    },
    'generate-monthly-reports': {
        'task': 'app.tasks.report_tasks.generate_monthly_reports',
        'schedule': 2592000.0,  # Every month (30 days)
    },
    'analyze-recent-posts': {
        'task': 'app.tasks.ai_tasks.analyze_recent_posts',
        'schedule': 7200.0,  # Every 2 hours
    },
}

