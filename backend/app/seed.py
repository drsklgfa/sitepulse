from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import ConditionType, ExtractionType, Monitor, Notification, User
from app.security import hash_password


def seed_demo(db: Session) -> None:
    settings = get_settings()
    user = db.scalar(select(User).where(User.email == "demo@sitepulse.local"))
    if user is None:
        user = User(
            email="demo@sitepulse.local",
            display_name="Conta demonstrativa",
            password_hash=hash_password("SitePulseDemo123!"),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    has_monitor = db.scalar(select(Monitor.id).where(Monitor.owner_id == user.id).limit(1))
    if has_monitor is None:
        base = settings.demo_target_base_url.rstrip("/")
        monitors = [
            Monitor(
                owner_id=user.id,
                name="Preço do notebook demonstrativo",
                description="Detecta qualquer alteração no preço da página controlada pelo Demo Lab.",
                url=f"{base}/product",
                selector="[data-testid='price']",
                extraction_type=ExtractionType.PRICE,
                condition_type=ConditionType.ANY_CHANGE,
                interval_minutes=30,
                next_run_at=datetime.now(timezone.utc),
            ),
            Monitor(
                owner_id=user.id,
                name="Disponibilidade do produto",
                description="Avisa quando o texto de disponibilidade mudar.",
                url=f"{base}/product",
                selector="[data-testid='availability']",
                extraction_type=ExtractionType.TEXT,
                condition_type=ConditionType.ANY_CHANGE,
                interval_minutes=15,
                next_run_at=datetime.now(timezone.utc),
            ),
            Monitor(
                owner_id=user.id,
                name="Página dinâmica com JavaScript",
                description="Exemplo pronto para o motor Playwright.",
                url=f"{base}/dynamic",
                selector="[data-testid='dynamic-price']",
                extraction_type=ExtractionType.PRICE,
                condition_type=ConditionType.PRICE_DROP,
                render_js=True,
                interval_minutes=60,
                is_active=False,
                next_run_at=datetime.now(timezone.utc),
            ),
        ]
        db.add_all(monitors)
        db.commit()
        db.add(
            Notification(
                monitor_id=monitors[0].id,
                channel="in_app",
                status="sent",
                title="Bem-vindo ao SitePulse",
                body="Use o Demo Lab para alterar o produto e executar uma verificação completa.",
            )
        )
        db.commit()
