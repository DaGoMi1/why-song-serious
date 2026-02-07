from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID

from sqlalchemy import BigInteger, String, Enum, Uuid, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AuthType(PyEnum):
    SPOTIFY = "SPOTIFY"
    GUEST = "GUEST"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(100), nullable=False)
    auth_type: Mapped[AuthType] = mapped_column(Enum(AuthType), nullable=False)
    guest_id: Mapped[Optional[UUID]] = mapped_column(Uuid, nullable=True)
    spotify_user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    # Relationships
    playlists: Mapped[list["Playlist"]] = relationship(back_populates="user")
    preferences: Mapped[list["UserPreference"]] = relationship(back_populates="user")
    interactions: Mapped[list["TrackInteraction"]] = relationship(back_populates="user")
