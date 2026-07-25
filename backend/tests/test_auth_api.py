def test_register_login_and_me(client) -> None:
    register = client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123!", "display_name": "Usuário"},
    )
    assert register.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "user@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 200

    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "user@example.com"


def test_rejects_bad_password(client) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "user@example.com", "password": "StrongPass123!", "display_name": "Usuário"},
    )
    response = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong"})
    assert response.status_code == 401
