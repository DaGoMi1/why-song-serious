from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.common.dependencies import get_current_user_id
from app.common.exceptions import NotFoundException
from app.domain.track.schema import (
    TrackSearchRequest,
    TrackSearchResponse,
    TrackResponse,
    TrackIdsRequest,
    SpotifyIdsRequest,
    TrackListResponse,
)
from app.domain.track.service import (
    save_user_preference,
    search_tracks_by_preference,
    get_track_by_id,
    get_tracks_by_ids,
    get_tracks_by_spotify_ids,
)
from app.domain.interaction.service import save_search_interactions

router = APIRouter(prefix="/tracks", tags=["tracks"])


@router.post("/search", response_model=TrackSearchResponse)
async def search_tracks(
    request: TrackSearchRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """
    취향 기반 트랙 검색

    1. 사용자 취향(preferences) 저장
    2. 유사한 트랙 검색
    3. 검색 결과 인터랙션 기록
    """
    raw_preferences = request.preferences.to_list()
    normalized_preferences = request.preferences.to_normalized_list()

    # 취향 저장 (raw 값)
    preference = await save_user_preference(db, user_id, raw_preferences)

    # 트랙 검색 (정규화된 값으로 벡터 검색)
    tracks = await search_tracks_by_preference(db, normalized_preferences, request.limit)

    # 검색 결과 인터랙션 기록
    await save_search_interactions(db, user_id, [track.id for track in tracks])
    await db.commit()
    
    return TrackSearchResponse(
        preference_id=preference.id,
        tracks=[TrackResponse.model_validate(track) for track in tracks],
    )


@router.post("/ids", response_model=TrackListResponse)
async def get_tracks_by_id_list(
    request: TrackIdsRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """트랙 ID 목록으로 조회"""
    tracks = await get_tracks_by_ids(db, request.track_ids)
    return TrackListResponse(
        tracks=[TrackResponse.model_validate(track) for track in tracks],
    )


@router.post("/spotify-ids", response_model=TrackListResponse)
async def get_tracks_by_spotify_id_list(
    request: SpotifyIdsRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Spotify 트랙 ID 목록으로 조회"""
    tracks = await get_tracks_by_spotify_ids(db, request.spotify_track_ids)
    return TrackListResponse(
        tracks=[TrackResponse.model_validate(track) for track in tracks],
    )


@router.get("/{track_id}", response_model=TrackResponse)
async def get_track(
    track_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """트랙 상세 조회"""
    track = await get_track_by_id(db, track_id)
    
    if not track:
        raise NotFoundException("Track not found")
    
    return TrackResponse.model_validate(track)
