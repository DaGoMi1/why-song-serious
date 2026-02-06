from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.interaction.model import TrackInteraction


async def save_search_interactions(
    db: AsyncSession,
    user_id: int,
    track_ids: list[int],
) -> None:
    interactions = [
        TrackInteraction(user_id=user_id, track_id=track_id)
        for track_id in track_ids
    ]
    db.add_all(interactions)
    await db.flush()


async def mark_as_played(
    db: AsyncSession,
    user_id: int,
    track_id: int,
) -> TrackInteraction | None:
    result = await db.execute(
        select(TrackInteraction)
        .where(
            TrackInteraction.user_id == user_id,
            TrackInteraction.track_id == track_id,
        )
        .order_by(TrackInteraction.created_at.desc())
        .limit(1)
    )
    interaction = result.scalar_one_or_none()

    if not interaction:
        return None

    interaction.is_played = True
    await db.commit()
    await db.refresh(interaction)
    return interaction


async def mark_as_selected(
    db: AsyncSession,
    user_id: int,
    track_ids: list[int],
) -> None:
    await db.execute(
        update(TrackInteraction)
        .where(
            TrackInteraction.user_id == user_id,
            TrackInteraction.track_id.in_(track_ids),
        )
        .values(is_selected=True)
    )
