from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, ARRAY, DECIMAL, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    preference_values: Mapped[list] = mapped_column(ARRAY(DECIMAL(3, 2)), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship(back_populates="preferences")
