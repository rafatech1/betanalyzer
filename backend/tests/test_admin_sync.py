import asyncio

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.deps import get_current_admin_user
from app.main import app
from app.routers import admin as admin_router


class _FakeAdmin:
    id = 1


@pytest.mark.asyncio
async def test_sync_triggers_both_jobs_and_returns_job_names(monkeypatch) -> None:
    calls: list[str] = []

    async def fake_fixtures_job() -> None:
        calls.append("update_fixtures")

    async def fake_odds_job() -> None:
        calls.append("update_odds")

    monkeypatch.setattr(admin_router, "update_fixtures_job", fake_fixtures_job)
    monkeypatch.setattr(admin_router, "update_odds_job", fake_odds_job)

    app.dependency_overrides[get_current_admin_user] = lambda: _FakeAdmin()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/admin/sync")
    finally:
        app.dependency_overrides.pop(get_current_admin_user, None)

    assert response.status_code == 200
    assert set(response.json()["jobs_triggered"]) == {"update_fixtures", "update_odds"}

    # As jobs são disparadas em background (fire-and-forget); dá um respiro
    # ao loop de eventos para garantir que rodaram antes de checar o efeito.
    await asyncio.sleep(0.05)
    assert set(calls) == {"update_fixtures", "update_odds"}


@pytest.mark.asyncio
async def test_sync_requires_admin_role() -> None:
    from app.core.deps import get_current_user
    from app.models.user import UserRole

    class _FakeRegularUser:
        id = 2
        role = UserRole.USER
        ativo = True

    app.dependency_overrides[get_current_user] = lambda: _FakeRegularUser()
    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post("/admin/sync")
    finally:
        app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_sync_requires_authentication() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/admin/sync")

    assert response.status_code == 401
