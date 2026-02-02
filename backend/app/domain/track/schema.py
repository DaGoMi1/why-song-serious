from pydantic import BaseModel, Field


class TrackSearchRequest(BaseModel):
    """취향 기반 트랙 검색 요청"""
    preferences: list[float] = Field(
        ...,
        min_length=6,
        max_length=6,
        description="6개의 음악적 특징 값 (0~100 범위, 서버에서 0~1로 정규화)"
    )
    limit: int = Field(default=20, ge=1, le=50, description="검색 결과 개수")


class TrackResponse(BaseModel):
    """트랙 응답"""
    id: int
    spotify_track_id: str
    name: str
    artist: str
    album: str | None
    duration_ms: int | None
    popularity: int | None
    image_url: str | None
    audio_features: list[float]

    class Config:
        from_attributes = True


class TrackSearchResponse(BaseModel):
    """취향 기반 트랙 검색 응답"""
    preference_id: int
    tracks: list[TrackResponse]
