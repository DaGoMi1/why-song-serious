from pydantic import BaseModel, Field, field_validator, model_validator
import json


# 데이터 기반 min/max 통계 (정규화용)
FEATURE_STATS = {
    "acousticness": {"min": 0.0, "max": 1.0},
    "valence": {"min": 0.0, "max": 1.0},
    "energy": {"min": 0.0, "max": 1.0},
    "danceability": {"min": 0.0, "max": 1.0},
    "loudness": {"min": -60.0, "max": 1.342},
    "tempo": {"min": 0.0, "max": 217.913},
}


class AudioFeatures(BaseModel):
    """음악적 특징 값 (raw 값)"""
    acousticness: float = Field(..., ge=0, le=1)
    valence: float = Field(..., ge=0, le=1)
    energy: float = Field(..., ge=0, le=1)
    danceability: float = Field(..., ge=0, le=1)
    loudness: float = Field(..., ge=-60, le=10)  # dB, 약간의 여유
    tempo: float = Field(..., ge=0, le=250)      # BPM, 약간의 여유

    def to_list(self) -> list[float]:
        """리스트로 변환 (순서 고정)"""
        return [
            self.acousticness,
            self.valence,
            self.energy,
            self.danceability,
            self.loudness,
            self.tempo,
        ]

    def to_normalized_list(self) -> list[float]:
        """Min-Max 정규화된 리스트로 변환 (DB 쿼리용)"""
        raw = self.to_list()
        keys = ["acousticness", "valence", "energy", "danceability", "loudness", "tempo"]
        
        normalized = []
        for i, key in enumerate(keys):
            stats = FEATURE_STATS[key]
            min_val, max_val = stats["min"], stats["max"]
            range_val = max_val - min_val
            if range_val == 0:
                normalized.append(0.0)
            else:
                norm = (raw[i] - min_val) / range_val
                # 0~1 범위로 클램핑
                norm = max(0.0, min(1.0, norm))
                normalized.append(round(norm, 6))
        
        return normalized

    @classmethod
    def from_list(cls, values: list[float]) -> "AudioFeatures":
        """리스트에서 생성 (raw 값)"""
        return cls(
            acousticness=values[0],
            valence=values[1],
            energy=values[2],
            danceability=values[3],
            loudness=values[4],
            tempo=values[5],
        )


class TrackSearchRequest(BaseModel):
    """취향 기반 트랙 검색 요청"""
    preferences: AudioFeatures
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
    audio_features: AudioFeatures

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def convert_raw_features(cls, data):
        """raw_features를 audio_features로 변환"""
        if hasattr(data, "__dict__"):
            # ORM 객체인 경우
            raw = data.raw_features
            if isinstance(raw, str):
                raw = json.loads(raw)
            return {
                "id": data.id,
                "spotify_track_id": data.spotify_track_id,
                "name": data.name,
                "artist": data.artist,
                "album": data.album,
                "duration_ms": data.duration_ms,
                "popularity": data.popularity,
                "image_url": data.image_url,
                "audio_features": AudioFeatures.from_list(raw),
            }
        return data


class TrackSearchResponse(BaseModel):
    """취향 기반 트랙 검색 응답"""
    preference_id: int
    tracks: list[TrackResponse]
