from sqlalchemy import select

from app.database import SessionLocal
from app.models import ConditionType, ExtractionType, Monitor, Notification, User
from app.security import hash_password
from app.services.monitor_runner import execute_monitor
from app.services.scraper import ScrapeResult


def test_runner_detects_second_change(monkeypatch) -> None:
    values = iter(["1000", "900"])

    def fake_scrape(_monitor):
        value = next(values)
        return ScrapeResult(value=value, raw_excerpt=value, http_status=200, duration_ms=12, final_url="http://demo")

    monkeypatch.setattr("app.services.monitor_runner.scrape_monitor", fake_scrape)

    with SessionLocal() as db:
        user = User(email="runner@example.com", display_name="Runner", password_hash=hash_password("StrongPass123!"))
        db.add(user)
        db.commit()
        db.refresh(user)
        monitor = Monitor(
            owner_id=user.id,
            name="Preço",
            url="http://localhost:8080/product",
            selector=".price",
            extraction_type=ExtractionType.PRICE,
            condition_type=ConditionType.PRICE_DROP,
        )
        db.add(monitor)
        db.commit()
        db.refresh(monitor)

        first = execute_monitor(db, monitor.id)
        second = execute_monitor(db, monitor.id)

        assert not first.alert_triggered
        assert second.changed
        assert second.alert_triggered
        assert db.scalar(select(Notification).where(Notification.run_id == second.id)) is not None
