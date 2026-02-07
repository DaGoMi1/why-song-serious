from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.track.model import Track
from app.domain.preference.model import UserPreference


async def save_user_preference(
    db: AsyncSession,
    user_id: int,
    raw_preferences: list[float],
) -> UserPreference:
    """사용자 취향 저장 (raw 값)"""
    preference = UserPreference(
        user_id=user_id,
        preference_values=raw_preferences,
    )
    
    db.add(preference)
    await db.commit()
    await db.refresh(preference)
    
    return preference


async def search_tracks_by_preference(
    db: AsyncSession,
    normalized_preferences: list[float],
    limit: int = 20,
) -> list[Track]:
    """
    취향 기반 트랙 검색
    
    norm_features 컬럼과 벡터 유사도 검색
    - <-> : 유클리디안 거리 (L2)
    - <=> : 코사인 거리
    - <#> : 내적 (음수, 작을수록 유사)
    
    Args:
        normalized_preferences: 이미 0~1로 정규화된 값
    """
    embedding_str = f"[{','.join(map(str, normalized_preferences))}]"
    
    query = text("""
        SELECT id, spotify_track_id, name, artist, album, 
               duration_ms, popularity, image_url, 
               raw_features, norm_features, embedding, cluster_id
        FROM tracks
        ORDER BY norm_features <-> :embedding
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
            raw_features=row.raw_features,
            norm_features=row.norm_features,
            embedding=row.embedding,
            cluster_id=row.cluster_id,
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


async def get_tracks_by_spotify_ids(
    db: AsyncSession, spotify_track_ids: list[str]
) -> list[Track]:
    """여러 spotify_track_id로 트랙 조회"""
    result = await db.execute(
        select(Track).where(Track.spotify_track_id.in_(spotify_track_ids))
    )
    return list(result.scalars().all())
