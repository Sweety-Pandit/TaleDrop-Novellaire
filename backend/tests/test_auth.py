def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_creates_unverified_reader_by_default(client, register_user):
    user = register_user(client)
    assert user["role"] == "READER"
    assert user["is_verified"] is False


def test_register_rejects_duplicate_email(client, register_user):
    user = register_user(client)
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "someoneelse",
            "display_name": "Someone Else",
            "email": user["_email"],
            "password": "AnotherPass123",
        },
    )
    assert response.status_code == 400


def test_register_rejects_admin_role(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "wannabeadmin",
            "display_name": "Wannabe Admin",
            "email": "wannabe@example.com",
            "password": "Password123",
            "role": "ADMIN",
        },
    )
    assert response.status_code == 422


def test_login_with_wrong_password_is_rejected(client, register_user):
    user = register_user(client)
    response = client.post(
        "/api/v1/auth/login",
        data={"username": user["_email"], "password": "wrong-password"},
    )
    assert response.status_code == 401


def test_login_returns_usable_access_token(client, register_user, auth_headers):
    user = register_user(client)
    headers = auth_headers(client, user["_email"], user["_password"])
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["email"] == user["_email"]


def test_refresh_token_issues_new_access_token(client, register_user):
    user = register_user(client)
    login = client.post(
        "/api/v1/auth/login",
        data={"username": user["_email"], "password": user["_password"]},
    )
    refresh_token = login.json()["refresh_token"]

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_unauthenticated_request_to_protected_route_is_rejected(client):
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401
