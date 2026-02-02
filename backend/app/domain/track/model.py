from typing import Optional

from sqlalchemy import BigInteger, String, Integer, ARRAY, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector

from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    spotify_track_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str] = mapped_column(String(500), nullable=False)
    album: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    popularity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    preview_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Audio features (6개 feature, 0.00~1.00)
    audio_features: Mapped[list] = mapped_column(ARRAY(DECIMAL(3, 2)), nullable=False)
    
    # Embeddings for vector search
    emb_deepfm: Mapped[list] = mapped_column(Vector(64), nullable=False)
    emb_cml: Mapped[list] = mapped_column(Vector(64), nullable=False)
