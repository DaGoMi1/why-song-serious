from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="playlists")
    playlist_tracks: Mapped[list["PlaylistTrack"]] = relationship(
        back_populates="playlist", order_by="PlaylistTrack.position"
    )


class PlaylistTrack(Base):
    __tablename__ = "playlist_tracks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    track_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tracks.id"), nullable=False)
    playlist_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("playlists.id"), nullable=False
    )

    # Relationships
    playlist: Mapped["Playlist"] = relationship(back_populates="playlist_tracks")
    track: Mapped["Track"] = relationship()
