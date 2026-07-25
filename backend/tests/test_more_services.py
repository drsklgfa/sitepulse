from decimal import Decimal

import pytest
from sqlalchemy import select

from app.database import SessionLocal
from app.models import ConditionType, ExtractionType, Monitor, RunStatus, User
from app.security import hash_password
from app.seed import seed_demo
from app.services.change_detection import evaluate_condition
from app.services.extractors import ExtractionError, content_hash, extract_content, parse_number
from app.services.monitor_runner import execute_monitor
from app.services.notifier import send_email
from app.services.scraper import ScrapeError, ScrapeResult, scrape_monitor


def test_remaining_conditions() -> None:
    assert evaluate_condition(condition=ConditionType.PRICE_BELOW, current_value='9', previous_value='10', changed=True, threshold=9.5)
    assert evaluate_condition(condition=ConditionType.CONTAINS, current_value='Vaga aberta', previous_value='Fechada', changed=True, keyword='aberta')
    assert evaluate_condition(condition=ConditionType.NOT_CONTAINS, current_value='Sem indisponibilidade', previous_value='x', changed=True, keyword='esgotado')
    assert evaluate_condition(condition=ConditionType.STATUS_NOT_OK, current_value='503', previous_value=None, changed=True)
    assert not evaluate_condition(condition=ConditionType.STATUS_NOT_OK, current_value='200', previous_value=None, changed=False)


def test_more_extractors() -> None:
    html = "<html><body><a class='item' data-id='42'><b>Olá</b></a></body></html>"
    status, _ = extract_content(html, selector=None, extraction_type=ExtractionType.STATUS, http_status=503)
    assert status == '503'
    attribute, _ = extract_content(html, selector='.item', extraction_type=ExtractionType.ATTRIBUTE, attribute_name='data-id')
    assert attribute == '42'
    markup, _ = extract_content(html, selector='.item', extraction_type=ExtractionType.HTML)
    assert '<a' in markup
    assert parse_number('1.234') == Decimal('1.234')
    assert len(content_hash('valor')) == 64
    with pytest.raises(ExtractionError):
        extract_content(html, selector='.item', extraction_type=ExtractionType.ATTRIBUTE)
    with pytest.raises(ExtractionError):
        parse_number('sem número')


def test_notifier_is_skipped_when_disabled() -> None:
    status, error = send_email('Assunto', 'Corpo')
    assert status == 'skipped'
    assert error is None


def test_scrape_monitor_with_mocked_fetch(monkeypatch) -> None:
    monitor = Monitor(
        owner_id=1,
        name='Preço',
        url='http://localhost:8080/product',
        selector='.price',
        extraction_type=ExtractionType.PRICE,
        condition_type=ConditionType.ANY_CHANGE,
    )
    monkeypatch.setattr('app.services.scraper._fetch_http', lambda _url: ("<span class='price'>R$ 99,90</span>", 200, 'http://demo'))
    result = scrape_monitor(monitor)
    assert result.value == '99.9'
    assert result.http_status == 200


def test_runner_failure_is_persisted(monkeypatch) -> None:
    monkeypatch.setattr('app.services.monitor_runner.scrape_monitor', lambda _monitor: (_ for _ in ()).throw(ScrapeError('offline')))
    with SessionLocal() as db:
        user = User(email='failure@example.com', display_name='Failure', password_hash=hash_password('StrongPass123!'))
        db.add(user)
        db.commit()
        db.refresh(user)
        monitor = Monitor(owner_id=user.id, name='Falha', url='http://localhost:8080/product', selector='body')
        db.add(monitor)
        db.commit()
        db.refresh(monitor)
        run = execute_monitor(db, monitor.id)
        assert run.status == RunStatus.FAILED
        assert run.error_message == 'offline'


def test_seed_is_idempotent() -> None:
    with SessionLocal() as db:
        seed_demo(db)
        seed_demo(db)
        users = db.scalars(select(User).where(User.email == 'demo@sitepulse.local')).all()
        monitors = db.scalars(select(Monitor).where(Monitor.owner_id == users[0].id)).all()
        assert len(users) == 1
        assert len(monitors) == 3
