from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.track.model import Track
from app.domain.preference.model import UserPreference


async def save_user_preference(
    db: AsyncSession,
    user_id: int,
    preferences: list[float],
) -> UserPreference:
    """사용자 취향 저장"""
    # 0~100 → 0~1 정규화
    normalized = [round(p / 100, 2) for p in preferences]
    
    preference = UserPreference(
        user_id=user_id,
        preference_values=normalized,
    )
    
    db.add(preference)
    await db.commit()
    await db.refresh(preference)
    
    return preference


async def search_tracks_by_preference(
    db: AsyncSession,
    preferences: list[float],
    limit: int = 20,
) -> list[Track]:
    """
    취향 기반 트랙 검색
    
    1. user_preferences 값을 audio_features 컬럼과 cosine similarity 검색
    """
    # 0~100 → 0~1 정규화
    normalized = [round(p / 100, 2) for p in preferences]
    
    # pgvector cosine distance 검색 (<=> 연산자)
    # cosine distance = 1 - cosine similarity, 작을수록 유사
    embedding_str = f"[{','.join(map(str, normalized))}]"
    
    query = text("""
        SELECT id, spotify_track_id, name, artist, album, 
               duration_ms, popularity, image_url, audio_features
        FROM tracks
        ORDER BY audio_features <=> :embedding
        LIMIT :limit
    """)
    
    result = await db.execute(query, {"embedding": embedding_str, "limit": limit})
    rows = result.fetchall()
    
    # Row를 Track 객체로 변환
    tracks = []
    for row in rows:
        track = Track(
            id=row.id,
            spotify_track_id=row.spotify_track_id,
            name=row.name,
            artist=row.artist,
            album=row.album,
            duration_ms=row.duration_ms,
            popularity=row.popularity,
            image_url=row.image_url,
            audio_features=row.audio_features,
        )
        tracks.append(track)
    
    return tracks


async def get_track_by_id(db: AsyncSession, track_id: int) -> Track | None:
    """ID로 트랙 조회"""
    result = await db.execute(select(Track).where(Track.id == track_id))
    return result.scalar_one_or_none()


async def get_tracks_by_ids(db: AsyncSession, track_ids: list[int]) -> list[Track]:
    """여러 ID로 트랙 조회"""
    result = await db.execute(select(Track).where(Track.id.in_(track_ids)))
    return list(result.scalars().all())
