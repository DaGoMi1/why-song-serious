from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.preference.model import UserPreference


async def get_latest_preference(db: AsyncSession, user_id: int) -> UserPreference | None:
    result = await db.execute(
        select(UserPreference)
        .where(UserPreference.user_id == user_id)
        .order_by(UserPreference.created_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()

