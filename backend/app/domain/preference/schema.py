from pydantic import BaseModel, model_validator

from app.domain.track.schema import AudioFeatures


class PreferenceResponse(BaseModel):
    preferences: AudioFeatures

    class Config:
        from_attributes = True

    @model_validator(mode="before")
    @classmethod
    def convert_preference_values(cls, data):
        if hasattr(data, "__dict__"):
            return {
                "preferences": AudioFeatures.from_list(
                    [float(v) for v in data.preference_values]
                ),
            }
        return data
