from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class TrackInteraction(Base):
    __tablename__ = "track_interactions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    is_played: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)
    track_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("tracks.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="interactions")
    track: Mapped["Track"] = relationship()
