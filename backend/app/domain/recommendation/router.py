from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.common.dependencies import get_current_user_id
from app.common.exceptions import NotFoundException
from app.domain.track.schema import TrackResponse
from app.domain.recommendation.schema import RecommendationRequest, RecommendationResponse
from app.domain.recommendation.service import create_recommendation, get_latest_recommendation

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", response_model=RecommendationResponse)
async def recommend_tracks(
    request: RecommendationRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """선택한 트랙 기반 추천 생성 및 플레이리스트 저장"""
    recommended, description = await create_recommendation(
        db, user_id, request.track_ids
    )

    return RecommendationResponse(
        tracks=[TrackResponse.model_validate(track) for track in recommended],
        description=description,
    )


@router.get("/latest", response_model=RecommendationResponse)
async def get_latest_user_recommendation(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """최근 추천 결과 조회"""
    result = await get_latest_recommendation(db, user_id)

    if not result:
        raise NotFoundException("No recommendation found")

    tracks, description = result

    return RecommendationResponse(
        tracks=[TrackResponse.model_validate(track) for track in tracks],
        description=description,
    )
