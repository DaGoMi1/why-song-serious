"""make track cluster_id not null

Revision ID: 003
Revises: 002
Create Date: 2025-02-04

이 마이그레이션은 모든 tracks에 cluster_id가 할당된 후 적용해야 합니다.
적용 전 확인: SELECT COUNT(*) FROM tracks WHERE cluster_id IS NULL;
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        'tracks',
        'cluster_id',
        existing_type=sa.BigInteger(),
        nullable=False
    )


def downgrade() -> None:
    op.alter_column(
        'tracks',
        'cluster_id',
        existing_type=sa.BigInteger(),
        nullable=True
    )
