"""add clusters table and track cluster_id

Revision ID: 002
Revises: 001
Create Date: 2025-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # clusters 테이블 생성
    op.create_table(
        'clusters',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('cluster_num', sa.Integer(), nullable=False),
        sa.Column('cluster_description', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cluster_num')
    )
    
    # tracks 테이블에 cluster_id 컬럼 추가 (nullable=True)
    op.add_column(
        'tracks',
        sa.Column('cluster_id', sa.BigInteger(), nullable=True)
    )
    
    # FK 제약조건 추가
    op.create_foreign_key(
        'fk_tracks_cluster_id',
        'tracks',
        'clusters',
        ['cluster_id'],
        ['id']
    )


def downgrade() -> None:
    # FK 제약조건 제거
    op.drop_constraint('fk_tracks_cluster_id', 'tracks', type_='foreignkey')
    
    # cluster_id 컬럼 제거
    op.drop_column('tracks', 'cluster_id')
    
    # clusters 테이블 제거
    op.drop_table('clusters')
