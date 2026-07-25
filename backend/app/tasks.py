from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import or_, select

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Monitor
from app.services.monitor_runner import execute_monitor


@celery_app.task(name="sitepulse.run_monitor", bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def run_monitor_task(self, monitor_id: int, run_id: int | None = None) -> int:
    with SessionLocal() as db:
        run = execute_monitor(db, monitor_id, run_id)
        return run.id


@celery_app.task(name="sitepulse.enqueue_due_monitors")
def enqueue_due_monitors() -> int:
    now = datetime.now(timezone.utc)
    with SessionLocal() as db:
        monitors = db.scalars(
            select(Monitor).where(
                Monitor.is_active.is_(True),
                or_(Monitor.next_run_at.is_(None), Monitor.next_run_at <= now),
            )
        ).all()
        for monitor in monitors:
            run_monitor_task.delay(monitor.id)
            monitor.next_run_at = now + timedelta(minutes=monitor.interval_minutes)
        db.commit()
        return len(monitors)
