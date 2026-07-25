from __future__ import annotations

from celery import Celery
from celery.schedules import crontab

from app.config import get_settings

settings = get_settings()
celery_app = Celery("sitepulse", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_always_eager=settings.celery_always_eager,
    beat_schedule={
        "enqueue-due-monitors-every-minute": {
            "task": "sitepulse.enqueue_due_monitors",
            "schedule": crontab(minute="*"),
        }
    },
)
celery_app.autodiscover_tasks(["app"])
