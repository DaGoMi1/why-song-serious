from enum import Enum

from pydantic import BaseModel, Field

from app.domain.track.schema import TrackResponse


class InferenceType(str, Enum):
    EMBEDDING = "embedding"
    MODEL_DEEPFM = "model-deepfm"
    MODEL_EASE = "model-ease"
    MODEL_LIGHTGCN = "model-lightgcn"

    def to_model_type(self) -> str:
        return self.value.removeprefix("model-")


class RecommendationRequest(BaseModel):
    inference_type: InferenceType = Field(
        default=InferenceType.EMBEDDING,
        description="추천 추론 방식",
    )
    track_ids: list[int] = Field(..., min_length=3, max_length=10, description="선택한 트랙 ID 목록")


class RecommendationResponse(BaseModel):
    tracks: list[TrackResponse]
    description: str
