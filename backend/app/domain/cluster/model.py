from sqlalchemy import BigInteger, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cluster_num: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    cluster_description: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    tracks: Mapped[list["Track"]] = relationship(back_populates="cluster")
