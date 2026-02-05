from typing import Optional

from sqlalchemy import BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database import Base


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    spotify_track_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    album: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    popularity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Audio features for vector search
    raw_features: Mapped[list] = mapped_column(Vector(6), nullable=False)
    norm_features: Mapped[list] = mapped_column(Vector(6), nullable=False)
    embedding: Mapped[list] = mapped_column(Vector(64), nullable=False)
    
    # Cluster FK
    cluster_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("clusters.id"), nullable=False
    )

    # Relationships
    cluster: Mapped["Cluster"] = relationship(back_populates="tracks")
