import re
from datetime import UTC, datetime, timedelta

from pwdlib.hashers.bcrypt import BcryptHasher

from app.modules.auth.models import PasswordResetCode
from tests.conftest import auth_headers

REGISTER_PAYLOAD = {
    "username": "yazarkullanici",
    "email": "Yazar@Example.com",
    "password": "Sifre1234",
    "password_confirm": "Sifre1234",
}


def test_register_creates_user_and_returns_token(client):
    response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    assert response.status_code == 201
    body = response.json()
    assert body["user"]["username"] == "yazarkullanici"
    assert body["user"]["email"] == "yazar@example.com"
    assert "access_token" in body


def test_register_duplicate_email_returns_409(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    other = {**REGISTER_PAYLOAD, "username": "baskakullanici"}
    response = client.post("/api/v1/auth/register", json=other)
    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_TAKEN"


def test_register_duplicate_username_returns_409(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    other = {**REGISTER_PAYLOAD, "email": "baska@example.com"}
    response = client.post("/api/v1/auth/register", json=other)
    assert response.status_code == 409
    assert response.json()["code"] == "USERNAME_TAKEN"


def test_register_password_mismatch_returns_422(client):
    payload = {**REGISTER_PAYLOAD, "password_confirm": "FarkliSifre1"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_weak_password_returns_422(client):
    payload = {**REGISTER_PAYLOAD, "password": "sadeceharf", "password_confirm": "sadeceharf"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_register_reserved_username_returns_422(client):
    payload = {**REGISTER_PAYLOAD, "username": "admin"}
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_with_email_and_username(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)

    by_email = client.post("/api/v1/auth/login", json={"login": "yazar@example.com", "password": "Sifre1234"})
    assert by_email.status_code == 200

    by_username = client.post("/api/v1/auth/login", json={"login": "yazarkullanici", "password": "Sifre1234"})
    assert by_username.status_code == 200


def test_login_wrong_password_returns_401(client):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    response = client.post("/api/v1/auth/login", json={"login": "yazarkullanici", "password": "YanlisSifre1"})
    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


def test_login_upgrades_bcrypt_hash_to_argon2(client, db, user_factory):
    user = user_factory(username="eskikullanici", email="eski@example.com", password="ignored")
    user.password_hash = BcryptHasher().hash("EskiSifre1")
    db.commit()
    assert user.password_hash.startswith("$2b$")

    response = client.post("/api/v1/auth/login", json={"login": "eskikullanici", "password": "EskiSifre1"})
    assert response.status_code == 200

    db.refresh(user)
    assert user.password_hash.startswith("$argon2")


def test_full_password_reset_flow_invalidates_old_token(client, db, monkeypatch):
    register_response = client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    old_token = register_response.json()["access_token"]

    sent_emails = []
    monkeypatch.setattr(
        "app.modules.auth.service.send_email",
        lambda to, subject, text, html=None: sent_emails.append(text) or True,
    )

    request_response = client.post("/api/v1/auth/password-reset/request", json={"email": "yazar@example.com"})
    assert request_response.status_code == 202
    assert len(sent_emails) == 1
    code = re.search(r"\d{6}", sent_emails[0]).group()

    verify_response = client.post(
        "/api/v1/auth/password-reset/verify", json={"email": "yazar@example.com", "code": code}
    )
    assert verify_response.status_code == 200
    assert verify_response.json() == {"valid": True}

    confirm_response = client.post(
        "/api/v1/auth/password-reset/confirm",
        json={
            "email": "yazar@example.com",
            "code": code,
            "new_password": "YeniSifre1",
            "new_password_confirm": "YeniSifre1",
        },
    )
    assert confirm_response.status_code == 200

    new_login = client.post(
        "/api/v1/auth/login", json={"login": "yazar@example.com", "password": "YeniSifre1"}
    )
    assert new_login.status_code == 200

    old_token_response = client.post(
        "/api/v1/auth/logout-all", headers={"Authorization": f"Bearer {old_token}"}
    )
    assert old_token_response.status_code == 401


def test_expired_reset_code_returns_400(client, db, monkeypatch):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    monkeypatch.setattr("app.modules.auth.service.send_email", lambda *a, **k: True)

    client.post("/api/v1/auth/password-reset/request", json={"email": "yazar@example.com"})
    reset_code = db.query(PasswordResetCode).order_by(PasswordResetCode.id.desc()).first()
    reset_code.expires_at = datetime.now(UTC) - timedelta(minutes=1)
    db.commit()

    response = client.post(
        "/api/v1/auth/password-reset/verify", json={"email": "yazar@example.com", "code": "000000"}
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CODE"


def test_reset_code_locks_after_five_wrong_attempts(client, monkeypatch):
    client.post("/api/v1/auth/register", json=REGISTER_PAYLOAD)
    monkeypatch.setattr("app.modules.auth.service.send_email", lambda *a, **k: True)
    client.post("/api/v1/auth/password-reset/request", json={"email": "yazar@example.com"})

    last_status = None
    for _ in range(5):
        response = client.post(
            "/api/v1/auth/password-reset/verify", json={"email": "yazar@example.com", "code": "000000"}
        )
        last_status = response.status_code
    assert last_status == 400

    locked_response = client.post(
        "/api/v1/auth/password-reset/verify", json={"email": "yazar@example.com", "code": "000000"}
    )
    assert locked_response.status_code == 429
    assert locked_response.json()["code"] == "TOO_MANY_ATTEMPTS"


def test_current_user_dependency_rejects_stale_token_version(db, user_factory):
    from app.core.errors import AppError
    from app.modules.users.deps import get_current_user

    user = user_factory(username="tokenversion", email="tv-user@example.com", password="Sifre1234")
    token = auth_headers(user)["Authorization"].removeprefix("Bearer ")

    user.token_version += 1
    db.commit()

    try:
        get_current_user(db, token)
    except AppError as exc:
        assert exc.code == "INVALID_TOKEN"
    else:
        raise AssertionError("beklenen AppError fırlatılmadı")
