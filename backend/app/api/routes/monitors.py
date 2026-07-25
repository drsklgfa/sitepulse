from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal, get_db
from app.deps import get_current_user
from app.models import Monitor, Run, RunStatus, User
from app.schemas import MonitorCreate, MonitorOut, MonitorUpdate, RunOut, RunQueued
from app.services.monitor_runner import execute_monitor
from app.services.url_safety import UnsafeUrlError, validate_target_url

router = APIRouter(prefix="/monitors", tags=["Monitores"])


def _owned_monitor(db: Session, monitor_id: int, user_id: int) -> Monitor:
    monitor = db.scalar(select(Monitor).where(Monitor.id == monitor_id, Monitor.owner_id == user_id))
    if monitor is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitor não encontrado")
    return monitor


def _run_in_background(monitor_id: int, run_id: int) -> None:
    with SessionLocal() as db:
        execute_monitor(db, monitor_id, run_id)


@router.get("", response_model=list[MonitorOut])
def list_monitors(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[Monitor]:
    return list(db.scalars(select(Monitor).where(Monitor.owner_id == current_user.id).order_by(Monitor.created_at.desc())).all())


@router.post("", response_model=MonitorOut, status_code=status.HTTP_201_CREATED)
def create_monitor(
    payload: MonitorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Monitor:
    settings = get_settings()
    try:
        validate_target_url(
            payload.url,
            allow_private_networks=settings.allow_private_networks,
            allowed_private_hosts=settings.allowed_private_hosts,
        )
    except UnsafeUrlError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    monitor = Monitor(owner_id=current_user.id, next_run_at=datetime.now(timezone.utc), **payload.model_dump())
    db.add(monitor)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.get("/{monitor_id}", response_model=MonitorOut)
def get_monitor(
    monitor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Monitor:
    return _owned_monitor(db, monitor_id, current_user.id)


@router.patch("/{monitor_id}", response_model=MonitorOut)
def update_monitor(
    monitor_id: int,
    payload: MonitorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Monitor:
    monitor = _owned_monitor(db, monitor_id, current_user.id)
    changes = payload.model_dump(exclude_unset=True)
    if "url" in changes:
        settings = get_settings()
        try:
            validate_target_url(
                changes["url"],
                allow_private_networks=settings.allow_private_networks,
                allowed_private_hosts=settings.allowed_private_hosts,
            )
        except UnsafeUrlError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    for field, value in changes.items():
        setattr(monitor, field, value)
    db.commit()
    db.refresh(monitor)
    return monitor


@router.delete("/{monitor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_monitor(
    monitor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Response:
    monitor = _owned_monitor(db, monitor_id, current_user.id)
    db.delete(monitor)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{monitor_id}/run", response_model=RunQueued, status_code=status.HTTP_202_ACCEPTED)
def run_monitor(
    monitor_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunQueued:
    monitor = _owned_monitor(db, monitor_id, current_user.id)
    run = Run(monitor_id=monitor.id, status=RunStatus.QUEUED)
    db.add(run)
    db.commit()
    db.refresh(run)

    settings = get_settings()
    if not settings.celery_always_eager:
        try:
            from app.tasks import run_monitor_task

            run_monitor_task.delay(monitor.id, run.id)
            return RunQueued(run_id=run.id, status="queued", execution_mode="celery")
        except (ImportError, OSError, RuntimeError):
            pass

    background_tasks.add_task(_run_in_background, monitor.id, run.id)
    return RunQueued(run_id=run.id, status="queued", execution_mode="background")


@router.get("/{monitor_id}/runs", response_model=list[RunOut])
def monitor_runs(
    monitor_id: int,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Run]:
    monitor = _owned_monitor(db, monitor_id, current_user.id)
    return list(
        db.scalars(
            select(Run).where(Run.monitor_id == monitor.id).order_by(Run.created_at.desc()).limit(min(limit, 200))
        ).all()
    )
