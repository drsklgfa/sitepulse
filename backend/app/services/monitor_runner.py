from __future__ import annotations

from datetime import datetime, timedelta, timezone
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Monitor, Notification, Run, RunStatus, Snapshot
from app.services.change_detection import evaluate_condition
from app.services.extractors import content_hash
from app.services.notifier import send_email
from app.services.scraper import ScrapeError, scrape_monitor


def _scrape_with_retries(db: Session, run: Run, monitor: Monitor):
    settings = get_settings()
    last_error: ScrapeError | None = None
    for attempt in range(1, settings.max_scrape_attempts + 1):
        run.attempts = attempt
        db.commit()
        try:
            return scrape_monitor(monitor)
        except ScrapeError as exc:
            last_error = exc
            if attempt < settings.max_scrape_attempts:
                time.sleep(settings.retry_backoff_seconds * attempt)
    assert last_error is not None
    raise last_error


def execute_monitor(db: Session, monitor_id: int, run_id: int | None = None) -> Run:
    monitor = db.scalar(select(Monitor).where(Monitor.id == monitor_id))
    if monitor is None:
        raise LookupError(f"Monitor {monitor_id} não encontrado")

    run = db.get(Run, run_id) if run_id else None
    if run is None:
        run = Run(monitor_id=monitor.id, status=RunStatus.QUEUED)
        db.add(run)
        db.commit()
        db.refresh(run)

    run.status = RunStatus.RUNNING
    run.started_at = datetime.now(timezone.utc)
    db.commit()

    try:
        result = _scrape_with_retries(db, run, monitor)
        new_hash = content_hash(result.value)
        previous_value = monitor.last_value
        changed = monitor.last_hash is not None and monitor.last_hash != new_hash
        alert_triggered = evaluate_condition(
            condition=monitor.condition_type,
            current_value=result.value,
            previous_value=previous_value,
            changed=changed,
            threshold=monitor.threshold,
            keyword=monitor.keyword,
        )

        run.status = RunStatus.CHANGED if changed else RunStatus.NO_CHANGE
        run.http_status = result.http_status
        run.duration_ms = result.duration_ms
        run.value = result.value
        run.previous_value = previous_value
        run.changed = changed
        run.alert_triggered = alert_triggered
        run.finished_at = datetime.now(timezone.utc)

        snapshot = Snapshot(
            monitor_id=monitor.id,
            run_id=run.id,
            value=result.value,
            content_hash=new_hash,
            raw_excerpt=result.raw_excerpt,
        )
        db.add(snapshot)

        monitor.last_value = result.value
        monitor.last_hash = new_hash
        monitor.last_checked_at = run.finished_at
        monitor.next_run_at = run.finished_at + timedelta(minutes=monitor.interval_minutes)

        if alert_triggered:
            title = f"Alteração detectada em {monitor.name}"
            body = f"Valor anterior: {previous_value or 'primeira captura'}\nValor atual: {result.value}\nURL: {monitor.url}"
            email_status, email_error = send_email(title, body)
            db.add(Notification(monitor_id=monitor.id, run_id=run.id, channel="in_app", status="sent", title=title, body=body))
            if email_status != "skipped":
                db.add(
                    Notification(
                        monitor_id=monitor.id,
                        run_id=run.id,
                        channel="email",
                        status=email_status,
                        title=title,
                        body=body if not email_error else f"{body}\n\nErro SMTP: {email_error}",
                    )
                )

        db.commit()
        db.refresh(run)
        return run
    except ScrapeError as exc:
        run.status = RunStatus.FAILED
        run.error_message = str(exc)
        run.finished_at = datetime.now(timezone.utc)
        monitor.last_checked_at = run.finished_at
        monitor.next_run_at = run.finished_at + timedelta(minutes=monitor.interval_minutes)
        db.commit()
        db.refresh(run)
        return run
