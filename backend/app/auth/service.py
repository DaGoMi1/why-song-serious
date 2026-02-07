from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.domain.user.model import User, AuthType

settings = get_settings()


def create_access_token(user_id: int) -> str:
    """JWT 액세스 토큰 생성"""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


async def create_guest_user(db: AsyncSession) -> User:
    """Guest 유저 생성"""
    guest_id = uuid4()
    nickname = f"Guest_{str(guest_id)[:8]}"
    
    user = User(
        nickname=nickname,
        auth_type=AuthType.GUEST,
        guest_id=guest_id,
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """ID로 유저 조회"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
