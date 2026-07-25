from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["Sistema"])


@router.get("/health", response_model=HealthResponse)
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    settings = get_settings()
    return HealthResponse(status="ok", app=settings.app_name, version=settings.app_version, database="ok")


@router.get("/demo-info")
def demo_info() -> dict[str, str]:
    settings = get_settings()
    return {
        "email": "demo@sitepulse.local",
        "password": "SitePulseDemo123!",
        "demo_target": settings.demo_target_base_url,
        "mailpit": "http://localhost:8025",
        "flower": "http://localhost:5555",
    }
