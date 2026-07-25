from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Monitor, Run, User
from app.schemas import RunOut

router = APIRouter(prefix="/runs", tags=["Execuções"])


@router.get("", response_model=list[RunOut])
def list_runs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Run]:
    query = (
        select(Run)
        .join(Monitor)
        .where(Monitor.owner_id == current_user.id)
        .order_by(Run.created_at.desc())
        .limit(min(limit, 300))
    )
    return list(db.scalars(query).all())


@router.get("/{run_id}", response_model=RunOut)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Run:
    run = db.scalar(select(Run).join(Monitor).where(Run.id == run_id, Monitor.owner_id == current_user.id))
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Execução não encontrada")
    return run
