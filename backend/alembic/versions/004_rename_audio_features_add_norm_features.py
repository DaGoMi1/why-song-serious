"""rename audio_features to raw_features and add norm_features

Revision ID: 004
Revises: 003
Create Date: 2025-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # audio_features -> raw_features 이름 변경
    op.alter_column(
        'tracks',
        'audio_features',
        new_column_name='raw_features'
    )
    
    # norm_features 컬럼 추가 (초기값 0 벡터)
    op.add_column(
        'tracks',
        sa.Column('norm_features', Vector(6), nullable=True)
    )
    
    # 초기값을 0 벡터로 설정
    op.execute("UPDATE tracks SET norm_features = '[0,0,0,0,0,0]'")
    
    # NOT NULL 제약 추가
    op.alter_column(
        'tracks',
        'norm_features',
        nullable=False
    )


def downgrade() -> None:
    # norm_features 컬럼 제거
    op.drop_column('tracks', 'norm_features')
    
    # raw_features -> audio_features 이름 복원
    op.alter_column(
        'tracks',
        'raw_features',
        new_column_name='audio_features'
    )
