from sqlalchemy import select

from app.database import SessionLocal
from app.models import Monitor, Notification, Run, RunStatus


def test_health_and_demo_info(client) -> None:
    health = client.get('/api/v1/health')
    assert health.status_code == 200
    assert health.json()['status'] == 'ok'
    info = client.get('/api/v1/demo-info')
    assert info.status_code == 200
    assert info.json()['email'] == 'demo@sitepulse.local'


def test_monitor_update_delete_and_dashboard(client, auth_headers) -> None:
    payload = {
        'name': 'Monitor editável',
        'url': 'http://localhost:8080/product',
        'selector': "[data-testid='price']",
        'extraction_type': 'price',
        'condition_type': 'any_change',
        'interval_minutes': 30,
    }
    created = client.post('/api/v1/monitors', json=payload, headers=auth_headers)
    monitor_id = created.json()['id']

    updated = client.patch(
        f'/api/v1/monitors/{monitor_id}',
        json={'name': 'Monitor atualizado', 'interval_minutes': 10},
        headers=auth_headers,
    )
    assert updated.status_code == 200
    assert updated.json()['name'] == 'Monitor atualizado'
    assert updated.json()['interval_minutes'] == 10

    dashboard = client.get('/api/v1/dashboard', headers=auth_headers)
    assert dashboard.status_code == 200
    assert dashboard.json()['total_monitors'] == 1

    deleted = client.delete(f'/api/v1/monitors/{monitor_id}', headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get(f'/api/v1/monitors/{monitor_id}', headers=auth_headers).status_code == 404


def test_runs_and_notifications_endpoints(client, auth_headers) -> None:
    created = client.post(
        '/api/v1/monitors',
        json={
            'name': 'Histórico',
            'url': 'http://localhost:8080/product',
            'selector': 'body',
            'extraction_type': 'text',
            'condition_type': 'any_change',
            'interval_minutes': 30,
        },
        headers=auth_headers,
    )
    monitor_id = created.json()['id']
    with SessionLocal() as db:
        run = Run(monitor_id=monitor_id, status=RunStatus.NO_CHANGE, value='ok', changed=False)
        db.add(run)
        db.commit()
        db.refresh(run)
        db.add(Notification(monitor_id=monitor_id, run_id=run.id, title='Teste', body='Alerta de teste'))
        db.commit()
        run_id = run.id

    runs = client.get('/api/v1/runs', headers=auth_headers)
    assert runs.status_code == 200
    assert runs.json()[0]['id'] == run_id
    assert client.get(f'/api/v1/runs/{run_id}', headers=auth_headers).status_code == 200
    notifications = client.get('/api/v1/notifications', headers=auth_headers)
    assert notifications.status_code == 200
    assert notifications.json()[0]['title'] == 'Teste'


def test_duplicate_registration_and_invalid_token(client) -> None:
    payload = {'email': 'duplicate@example.com', 'password': 'StrongPass123!', 'display_name': 'Duplicado'}
    assert client.post('/api/v1/auth/register', json=payload).status_code == 201
    assert client.post('/api/v1/auth/register', json=payload).status_code == 409
    assert client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer invalid'}).status_code == 401
