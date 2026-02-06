from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.common.dependencies import get_current_user_id
from app.common.exceptions import NotFoundException
from app.domain.preference.schema import PreferenceResponse
from app.domain.preference.service import get_latest_preference

router = APIRouter(prefix="/preferences", tags=["preferences"])


@router.get("/latest", response_model=PreferenceResponse)
async def get_latest_user_preference(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """최근 취향 조회"""
    preference = await get_latest_preference(db, user_id)

    if not preference:
        raise NotFoundException("No preference found")

    return preference
