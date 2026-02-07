from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.common.dependencies import get_current_user_id
from app.common.exceptions import NotFoundException
from app.domain.interaction.schema import PlayRequest
from app.domain.interaction.service import mark_as_played

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("/play")
async def play_track(
    request: PlayRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """트랙 재생 기록"""
    interaction = await mark_as_played(db, user_id, request.track_id)

    if not interaction:
        raise NotFoundException("Interaction not found")

    return {"message": "Play recorded"}
