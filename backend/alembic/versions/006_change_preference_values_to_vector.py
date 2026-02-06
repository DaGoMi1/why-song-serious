"""change preference_values to vector type

Revision ID: 006
Revises: 005
Create Date: 2025-02-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 기존 ARRAY(DECIMAL) 컬럼 제거 후 Vector(6)로 재생성
    op.drop_column('user_preferences', 'preference_values')
    op.add_column(
        'user_preferences',
        sa.Column('preference_values', Vector(6), nullable=False)
    )


def downgrade() -> None:
    op.drop_column('user_preferences', 'preference_values')
    op.add_column(
        'user_preferences',
        sa.Column('preference_values', sa.ARRAY(sa.DECIMAL(precision=3, scale=2)), nullable=False)
    )

