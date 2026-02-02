from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.common.dependencies import get_current_user_id
from app.auth.service import create_guest_user, create_access_token, get_user_by_id
from app.auth.schema import GuestLoginResponse, UserResponse
from app.common.exceptions import NotFoundException

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/guest", response_model=GuestLoginResponse)
async def guest_login(db: AsyncSession = Depends(get_db)):
    """Guest 로그인 - 새 유저 생성 후 토큰 발급"""
    user = await create_guest_user(db)
    access_token = create_access_token(user.id)
    
    return GuestLoginResponse(
        access_token=access_token,
        user_id=user.id,
        nickname=user.nickname,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """현재 로그인한 유저 정보 조회"""
    user = await get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException("User not found")
    
    return UserResponse(
        id=user.id,
        nickname=user.nickname,
        auth_type=user.auth_type.value,
        created_at=user.created_at,
    )


# TODO: Spotify OAuth 엔드포인트 (후순위)
# @router.get("/spotify")
# @router.get("/spotify/callback")
