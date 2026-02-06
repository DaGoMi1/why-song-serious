from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.track.service import get_tracks_by_ids
from app.domain.track.model import Track
from app.domain.playlist.model import Playlist, PlaylistTrack
from app.domain.recommendation.strategy import run_embedding_pipeline
from app.common.exceptions import BadRequestException


RECOMMENDATION_COUNT = 10


async def create_recommendation(
    db: AsyncSession,
    user_id: int,
    track_ids: list[int],
) -> tuple[list[Track], str]:
    input_tracks = await get_tracks_by_ids(db, track_ids)

    if len(input_tracks) != len(track_ids):
        raise BadRequestException("Some track IDs are invalid")

    recommended, description = await run_embedding_pipeline(
        db, input_tracks, RECOMMENDATION_COUNT
    )

    await save_as_playlist(db, user_id, description, recommended)

    return recommended, description


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
