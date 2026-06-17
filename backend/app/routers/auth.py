from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.db.redis import redis_client
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserOut
from app.services.auth_rate_limit import (
    clear_attempts,
    ensure_not_rate_limited,
    register_failed_attempt,
)
from app.services.auth_repo import get_user_by_email
from app.services.auth_tokens import (
    get_refresh_token_user_id,
    revoke_refresh_token,
    store_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

_REFRESH_COOKIE = "refresh_token"
_REFRESH_COOKIE_PATH = "/auth"


def _client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"


def _set_refresh_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        _REFRESH_COOKIE,
        token,
        httponly=True,
        samesite="lax",
        secure=settings.refresh_cookie_secure,
        max_age=settings.refresh_token_expire_days * 86400,
        path=_REFRESH_COOKIE_PATH,
    )


async def _issue_tokens(response: Response, user: User) -> TokenResponse:
    access_token = create_access_token(user.id, user.role.value)
    refresh_token, jti = create_refresh_token(user.id)
    await store_refresh_token(
        redis_client, jti, user.id, settings.refresh_token_expire_days * 86400
    )
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(
        access_token=access_token, expires_in=settings.access_token_expire_minutes * 60
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    ip = _client_ip(request)
    await ensure_not_rate_limited(redis_client, ip)

    user = await get_user_by_email(db, payload.email)
    if user is None or not user.ativo or not verify_password(payload.senha, user.senha_hash):
        await register_failed_attempt(redis_client, ip)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    await clear_attempts(redis_client, ip)
    return await _issue_tokens(response, user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request, response: Response, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    token = request.cookies.get(_REFRESH_COOKIE)
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token ausente")

    payload = decode_token(token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Token inválido")

    jti = payload.get("jti")
    stored_user_id = await get_refresh_token_user_id(redis_client, jti)
    if stored_user_id is None or stored_user_id != int(payload["sub"]):
        raise HTTPException(status_code=401, detail="Refresh token inválido ou revogado")

    user = await db.get(User, stored_user_id)
    if user is None or not user.ativo:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    await revoke_refresh_token(redis_client, jti)
    return await _issue_tokens(response, user)


@router.post("/logout", status_code=204)
async def logout(request: Request, response: Response) -> Response:
    token = request.cookies.get(_REFRESH_COOKIE)
    if token:
        try:
            payload = decode_token(token)
            jti = payload.get("jti")
            if jti:
                await revoke_refresh_token(redis_client, jti)
        except HTTPException:
            pass

    response.delete_cookie(_REFRESH_COOKIE, path=_REFRESH_COOKIE_PATH)
    response.status_code = 204
    return response


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
