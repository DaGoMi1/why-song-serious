from pydantic import BaseModel


class PlayRequest(BaseModel):
    track_id: int