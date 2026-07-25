from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Monitor, Notification, User
from app.schemas import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notificações"])


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Notification]:
    query = (
        select(Notification)
        .join(Monitor)
        .where(Monitor.owner_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(min(limit, 300))
    )
    return list(db.scalars(query).all())
