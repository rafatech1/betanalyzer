from datetime import datetime, timedelta, timezone

import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.db.session import get_db
from app.main import app
from app.models.user import User, UserRole
from app.routers import auth as auth_router
from app.schemas.auth import RegisterRequest, ResetPasswordRequest


def _fake_user(user_id: int = 1, email: str = "user@example.com", ativo: bool = True) -> User:
    return User(
        id=user_id,
        nome="Usuário Teste",
        email=email,
        senha_hash="hash",
        role=UserRole.USER,
        ativo=ativo,
    )


async def _override_get_db():
    yield None


@pytest.fixture(autouse=True)
def _no_real_db():
    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


def test_register_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        RegisterRequest(nome="Ana", email="ana@example.com", senha="short")


def test_register_request_accepts_password_with_8_chars() -> None:
    payload = RegisterRequest(nome="Ana", email="ana@example.com", senha="12345678")
    assert payload.senha == "12345678"


def test_reset_password_request_rejects_short_password() -> None:
    with pytest.raises(ValidationError):
        ResetPasswordRequest(token="abc", senha="short")


@pytest.mark.asyncio
async def test_register_returns_token_for_new_email(monkeypatch) -> None:
    created = _fake_user()

    async def fake_get_user_by_email(db, email):
        return None

    async def fake_create_user(db, nome, email, senha):
        return created

    async def fake_store_refresh_token(redis, jti, user_id, ttl_seconds):
        return None

    monkeypatch.setattr(auth_router, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_router, "create_user", fake_create_user)
    monkeypatch.setattr(auth_router, "store_refresh_token", fake_store_refresh_token)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={"nome": "Ana", "email": "ana@example.com", "senha": "12345678"},
        )

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body


@pytest.mark.asyncio
async def test_register_conflicts_when_email_already_exists(monkeypatch) -> None:
    async def fake_get_user_by_email(db, email):
        return _fake_user()

    monkeypatch.setattr(auth_router, "get_user_by_email", fake_get_user_by_email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={"nome": "Ana", "email": "ana@example.com", "senha": "12345678"},
        )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_rejects_password_shorter_than_8_chars() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/register",
            json={"nome": "Ana", "email": "ana@example.com", "senha": "short"},
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_forgot_password_returns_204_when_email_does_not_exist(monkeypatch) -> None:
    calls: list[str] = []

    async def fake_get_user_by_email(db, email):
        return None

    async def fake_send_email(to, subject, html):
        calls.append(to)

    monkeypatch.setattr(auth_router, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_router, "send_email", fake_send_email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/forgot-password", json={"email": "ghost@example.com"}
        )

    assert response.status_code == 204
    assert calls == []


@pytest.mark.asyncio
async def test_forgot_password_sends_email_when_user_exists(monkeypatch) -> None:
    sent: list[str] = []

    async def fake_get_user_by_email(db, email):
        return _fake_user(email=email)

    async def fake_create_password_reset_token(db, user_id, token, expires_at):
        return None

    async def fake_send_email(to, subject, html):
        sent.append(to)

    monkeypatch.setattr(auth_router, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(
        auth_router, "create_password_reset_token", fake_create_password_reset_token
    )
    monkeypatch.setattr(auth_router, "send_email", fake_send_email)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/forgot-password", json={"email": "user@example.com"}
        )

    assert response.status_code == 204
    assert sent == ["user@example.com"]


class _FakeTokenRow:
    def __init__(self, user_id: int, expires_at: datetime, used: bool = False) -> None:
        self.user_id = user_id
        self.expires_at = expires_at
        self.used = used


@pytest.mark.asyncio
async def test_reset_password_rejects_unknown_token(monkeypatch) -> None:
    async def fake_get_password_reset_token(db, token):
        return None

    monkeypatch.setattr(auth_router, "get_password_reset_token", fake_get_password_reset_token)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/reset-password", json={"token": "nope", "senha": "12345678"}
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_rejects_expired_token(monkeypatch) -> None:
    expired = _FakeTokenRow(user_id=1, expires_at=datetime.now(timezone.utc) - timedelta(hours=1))

    async def fake_get_password_reset_token(db, token):
        return expired

    monkeypatch.setattr(auth_router, "get_password_reset_token", fake_get_password_reset_token)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/reset-password", json={"token": "expired", "senha": "12345678"}
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_rejects_already_used_token(monkeypatch) -> None:
    used = _FakeTokenRow(
        user_id=1, expires_at=datetime.now(timezone.utc) + timedelta(hours=1), used=True
    )

    async def fake_get_password_reset_token(db, token):
        return used

    monkeypatch.setattr(auth_router, "get_password_reset_token", fake_get_password_reset_token)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/reset-password", json={"token": "used", "senha": "12345678"}
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_reset_password_succeeds_with_valid_token(monkeypatch) -> None:
    valid = _FakeTokenRow(user_id=1, expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    target_user = _fake_user(user_id=1)
    updated: list[str] = []
    marked_used: list[_FakeTokenRow] = []

    async def fake_get_password_reset_token(db, token):
        return valid

    async def fake_get(model, user_id):
        return target_user

    async def fake_update_user_password(db, user, nova_senha):
        updated.append(nova_senha)

    async def fake_mark_used(db, row):
        marked_used.append(row)

    monkeypatch.setattr(auth_router, "get_password_reset_token", fake_get_password_reset_token)
    monkeypatch.setattr(auth_router, "update_user_password", fake_update_user_password)
    monkeypatch.setattr(auth_router, "mark_password_reset_token_used", fake_mark_used)

    async def fake_db_get_override():
        class _Db:
            async def get(self, model, user_id):
                return target_user

        yield _Db()

    app.dependency_overrides[get_db] = fake_db_get_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/auth/reset-password", json={"token": "valid", "senha": "novaSenha123"}
        )

    assert response.status_code == 204
    assert updated == ["novaSenha123"]
    assert marked_used == [valid]
