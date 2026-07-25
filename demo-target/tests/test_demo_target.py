from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_product_has_scrape_targets() -> None:
    response = client.get('/product')
    assert response.status_code == 200
    assert 'data-testid="price"' in response.text
    assert 'data-testid="availability"' in response.text


def test_state_can_change_and_reset() -> None:
    changed = client.post('/api/state', json={'price': 1999.9, 'available': False})
    assert changed.status_code == 200
    assert changed.json()['price'] == 1999.9
    assert client.post('/api/reset').json()['price'] == 2499.9
