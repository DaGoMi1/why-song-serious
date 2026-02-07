from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.track.service import get_tracks_by_ids, get_tracks_by_spotify_ids
from app.domain.track.model import Track
from app.domain.playlist.model import Playlist, PlaylistTrack
from app.domain.recommendation.strategy import run_embedding_pipeline
from app.domain.recommendation.client import request_model_recommendation
from app.domain.recommendation.schema import InferenceType
from app.domain.interaction.service import mark_as_selected
from app.common.exceptions import BadRequestException


RECOMMENDATION_COUNT = 10


async def create_recommendation(
    db: AsyncSession,
    user_id: int,
    track_ids: list[int],
    inference_type: InferenceType = InferenceType.EMBEDDING,
) -> tuple[list[Track], str]:
    input_tracks = await get_tracks_by_ids(db, track_ids)

    if len(input_tracks) != len(track_ids):
        raise BadRequestException("Some track IDs are invalid")

    if inference_type == InferenceType.EMBEDDING:
        recommended, description = await run_embedding_pipeline(
            db, input_tracks, RECOMMENDATION_COUNT
        )
    else:
        recommended = await run_model_pipeline(
            db, input_tracks, inference_type
        )
        description = await _generate_description_for(db, recommended)

    await mark_as_selected(db, user_id, track_ids)
    await save_as_playlist(db, user_id, description, recommended)

    return recommended, description


async def run_model_pipeline(
    db: AsyncSession,
    input_tracks: list[Track],
    inference_type: InferenceType,
) -> list[Track]:
    spotify_ids = [track.spotify_track_id for track in input_tracks]
    model_type = inference_type.to_model_type()

    data = await request_model_recommendation(model_type, spotify_ids)

    scored_spotify_ids = sorted(data, key=lambda d: d["model_score"], reverse=True)
    ordered_ids = [item["id"] for item in scored_spotify_ids]

    tracks = await get_tracks_by_spotify_ids(db, ordered_ids)
    track_map = {track.spotify_track_id: track for track in tracks}

    return [track_map[sid] for sid in ordered_ids if sid in track_map]


async def _generate_description_for(
    db: AsyncSession, tracks: list[Track]
) -> str:
    from app.domain.recommendation.strategy import generate_description
    return await generate_description(db, tracks)


async def save_as_playlist(
    db: AsyncSession,
    user_id: int,
    name: str,
    tracks: list[Track],
) -> Playlist:
    playlist = Playlist(name=name, user_id=user_id)
    db.add(playlist)
    await db.flush()

    for position, track in enumerate(tracks):
        playlist_track = PlaylistTrack(
            playlist_id=playlist.id,
            track_id=track.id,
            position=position,
        )
        db.add(playlist_track)

    await db.commit()
    await db.refresh(playlist)
    return playlist


async def get_latest_recommendation(
    db: AsyncSession,
    user_id: int,
) -> tuple[list[Track], str] | None:
    result = await db.execute(
        select(Playlist)
        .where(Playlist.user_id == user_id)
        .order_by(Playlist.created_at.desc())
        .limit(1)
    )
    playlist = result.scalar_one_or_none()

    if not playlist:
        return None

    pt_result = await db.execute(
        select(PlaylistTrack)
        .where(PlaylistTrack.playlist_id == playlist.id)
        .order_by(PlaylistTrack.position)
    )
    playlist_tracks = list(pt_result.scalars().all())

    track_ids = [pt.track_id for pt in playlist_tracks]
    tracks = await get_tracks_by_ids(db, track_ids)

    track_map = {track.id: track for track in tracks}
    ordered_tracks = [track_map[tid] for tid in track_ids if tid in track_map]

    return ordered_tracks, playlist.name
