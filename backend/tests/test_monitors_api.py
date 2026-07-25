def test_create_and_list_monitor(client, auth_headers) -> None:
    payload = {
        "name": "Preço de demonstração",
        "description": "Monitor de teste",
        "url": "http://localhost:8080/product",
        "selector": "[data-testid='price']",
        "extraction_type": "price",
        "condition_type": "any_change",
        "interval_minutes": 30,
    }
    created = client.post("/api/v1/monitors", json=payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["name"] == payload["name"]

    listed = client.get("/api/v1/monitors", headers=auth_headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_monitor_requires_authentication(client) -> None:
    assert client.get("/api/v1/monitors").status_code == 401
