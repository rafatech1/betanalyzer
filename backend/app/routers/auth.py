import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.deps import get_current_user
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.db.redis import redis_client
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
    TokenResponse,
)
from app.schemas.user import UserOut
from app.services.auth_rate_limit import (
    clear_attempts,
    ensure_not_rate_limited,
    register_failed_attempt,
)
from app.services.auth_repo import create_user, get_user_by_email, update_user_password
from app.services.auth_tokens import (
    get_refresh_token_user_id,
    revoke_refresh_token,
    store_refresh_token,
)
from app.services.email.resend_client import send_email
from app.services.email.templates import build_password_reset_email_html
from app.services.password_reset_repo import (
    create_password_reset_token,
    get_password_reset_token,
    mark_password_reset_token_used,
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


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    existing = await get_user_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    user = await create_user(db, nome=payload.nome, email=payload.email, senha=payload.senha)
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


@router.post("/forgot-password", status_code=204)
async def forgot_password(
    payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)
) -> None:
    # Sempre responde 204, exista ou não o email — evita enumeração de
    # usuários cadastrados via timing/diferença de resposta.
    user = await get_user_by_email(db, payload.email)
    if user is None or not user.ativo:
        return

    token = uuid.uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(
        hours=settings.password_reset_token_expire_hours
    )
    await create_password_reset_token(db, user.id, token, expires_at)

    reset_url = f"{settings.frontend_url}/reset-password?token={token}"
    await send_email(
        user.email,
        "Redefinição de senha — BetAnalyzer",
        build_password_reset_email_html(reset_url),
    )


@router.post("/reset-password", status_code=204)
async def reset_password(
    payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)
) -> None:
    token_row = await get_password_reset_token(db, payload.token)
    if (
        token_row is None
        or token_row.used
        or token_row.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    user = await db.get(User, token_row.user_id)
    if user is None:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    await update_user_password(db, user, payload.senha)
    await mark_password_reset_token_used(db, token_row)
