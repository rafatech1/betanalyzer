from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.security import hash_password
from app.models.user import User, UserRole

logger = get_logger(__name__)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def seed_admin_user(db: AsyncSession) -> None:
    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        logger.warning("admin_seed_skipped_missing_env")
        return

    existing = await get_user_by_email(db, settings.admin_email)
    if existing is not None:
        return

    user = User(
        nome="Admin",
        email=settings.admin_email,
        senha_hash=hash_password(settings.admin_password),
        role=UserRole.ADMIN,
        ativo=True,
    )
    db.add(user)
    await db.commit()
    logger.info("admin_seeded", email=settings.admin_email)
