from dataclasses import dataclass

import pytest
from fastapi import HTTPException

from app.core.deps import get_current_admin_user
from app.models.user import UserRole


@dataclass
class _FakeUser:
    id: int
    role: UserRole


@pytest.mark.asyncio
async def test_admin_user_passes_through() -> None:
    admin = _FakeUser(id=1, role=UserRole.ADMIN)
    result = await get_current_admin_user(current_user=admin)  # type: ignore[arg-type]
    assert result is admin


@pytest.mark.asyncio
async def test_non_admin_user_raises_403() -> None:
    regular_user = _FakeUser(id=2, role=UserRole.USER)
    with pytest.raises(HTTPException) as exc_info:
        await get_current_admin_user(current_user=regular_user)  # type: ignore[arg-type]
    assert exc_info.value.status_code == 403
