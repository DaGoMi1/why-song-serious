"""initial schema

Revision ID: 001
Revises: 
Create Date: 2025-02-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgvector 확장 활성화
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # users 테이블
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('nickname', sa.String(length=100), nullable=False),
        sa.Column('auth_type', sa.Enum('SPOTIFY', 'GUEST', name='authtype'), nullable=False),
        sa.Column('guest_id', sa.Uuid(), nullable=True),
        sa.Column('spotify_user_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # tracks 테이블
    op.create_table(
        'tracks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('spotify_track_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('artist', sa.String(), nullable=False),
        sa.Column('album', sa.String(length=500), nullable=True),
        sa.Column('duration_ms', sa.Integer(), nullable=True),
        sa.Column('popularity', sa.Integer(), nullable=True),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('audio_features', Vector(6), nullable=False),
        sa.Column('embedding', Vector(64), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('spotify_track_id')
    )
    
    # playlists 테이블
    op.create_table(
        'playlists',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # playlist_tracks 테이블
    op.create_table(
        'playlist_tracks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('track_id', sa.BigInteger(), nullable=False),
        sa.Column('playlist_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['playlist_id'], ['playlists.id']),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # user_preferences 테이블
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('preference_values', sa.ARRAY(sa.DECIMAL(precision=3, scale=2)), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # track_interactions 테이블
    op.create_table(
        'track_interactions',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('is_played', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_selected', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('track_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['track_id'], ['tracks.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('track_interactions')
    op.drop_table('user_preferences')
    op.drop_table('playlist_tracks')
    op.drop_table('playlists')
    op.drop_table('tracks')
    op.drop_table('users')
    
    # Enum 타입 삭제
    op.execute('DROP TYPE IF EXISTS authtype')
