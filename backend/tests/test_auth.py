from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_and_login():
    # Register
    resp = client.post(
        "/api/auth/register",
        json={"email": "test@example.com", "password": "password123", "preferred_language": "de"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"

    # Login
    resp = client.post("/api/auth/login", json={"email": "test@example.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_logout_clears_cookie():
    client.post(
        "/api/auth/register",
        json={"email": "logout@example.com", "password": "password123", "preferred_language": "de"},
    )

    # Cookie should be set by register (and also by login, but register is enough).
    assert client.cookies.get("access_token")

    resp = client.post("/api/auth/logout")
    assert resp.status_code == 204

    # TestClient should remove cookie when receiving delete_cookie.
    assert not client.cookies.get("access_token")


def test_register_duplicate_email():
    client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "password123", "preferred_language": "de"},
    )
    resp = client.post(
        "/api/auth/register",
        json={"email": "dup@example.com", "password": "password123", "preferred_language": "de"},
    )
    assert resp.status_code == 400


def test_login_invalid_credentials():
    resp = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "wrongpass"})
    assert resp.status_code == 401
