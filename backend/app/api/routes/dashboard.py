from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Monitor, Notification, Run, RunStatus, User
from app.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardSummary)
def dashboard(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> DashboardSummary:
    monitor_filter = Monitor.owner_id == current_user.id
    total_monitors = db.scalar(select(func.count(Monitor.id)).where(monitor_filter)) or 0
    active_monitors = db.scalar(select(func.count(Monitor.id)).where(monitor_filter, Monitor.is_active.is_(True))) or 0

    run_stats = db.execute(
        select(
            func.count(Run.id),
            func.sum(case((Run.status != RunStatus.FAILED, 1), else_=0)),
            func.sum(case((Run.status == RunStatus.CHANGED, 1), else_=0)),
            func.sum(case((Run.status == RunStatus.FAILED, 1), else_=0)),
            func.avg(Run.duration_ms),
        )
        .join(Monitor)
        .where(monitor_filter)
    ).one()
    total_runs = int(run_stats[0] or 0)
    successful_runs = int(run_stats[1] or 0)
    changed_runs = int(run_stats[2] or 0)
    failed_runs = int(run_stats[3] or 0)
    average_duration_ms = int(run_stats[4] or 0)
    notification_count = db.scalar(select(func.count(Notification.id)).join(Monitor).where(monitor_filter)) or 0

    recent_runs = list(
        db.scalars(select(Run).join(Monitor).where(monitor_filter).order_by(Run.created_at.desc()).limit(8)).all()
    )
    recent_notifications = list(
        db.scalars(
            select(Notification).join(Monitor).where(monitor_filter).order_by(Notification.created_at.desc()).limit(6)
        ).all()
    )
    return DashboardSummary(
        total_monitors=total_monitors,
        active_monitors=active_monitors,
        total_runs=total_runs,
        successful_runs=successful_runs,
        changed_runs=changed_runs,
        failed_runs=failed_runs,
        unread_notifications=notification_count,
        success_rate=round((successful_runs / total_runs * 100) if total_runs else 100.0, 1),
        average_duration_ms=average_duration_ms,
        recent_runs=recent_runs,
        recent_notifications=recent_notifications,
    )
