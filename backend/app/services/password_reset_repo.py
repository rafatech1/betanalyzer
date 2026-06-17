from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.password_reset_token import PasswordResetToken


async def create_password_reset_token(
    db: AsyncSession, user_id: int, token: str, expires_at: datetime
) -> PasswordResetToken:
    row = PasswordResetToken(user_id=user_id, token=token, expires_at=expires_at, used=False)
    db.add(row)
    await db.commit()
    return row


async def get_password_reset_token(db: AsyncSession, token: str) -> PasswordResetToken | None:
    stmt = select(PasswordResetToken).where(PasswordResetToken.token == token)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def mark_password_reset_token_used(db: AsyncSession, row: PasswordResetToken) -> None:
    row.used = True
    await db.commit()
