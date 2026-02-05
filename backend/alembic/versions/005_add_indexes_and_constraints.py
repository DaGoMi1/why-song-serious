"""add indexes and constraints

Revision ID: 005
Revises: 004
Create Date: 2025-02-05

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # =====================
    # users 테이블
    # =====================
    # guest_id UNIQUE (인덱스 자동 생성)
    op.create_unique_constraint('uq_users_guest_id', 'users', ['guest_id'])
    
    # spotify_user_id UNIQUE (인덱스 자동 생성)
    op.create_unique_constraint('uq_users_spotify_user_id', 'users', ['spotify_user_id'])
    
    # =====================
    # tracks 테이블
    # =====================
    # norm_features HNSW (L2 - 유클리디안 거리)
    op.execute("""
        CREATE INDEX ix_tracks_norm_features_l2 
        ON tracks 
        USING hnsw (norm_features vector_l2_ops)
    """)
    
    # embedding HNSW (내적)
    op.execute("""
        CREATE INDEX ix_tracks_embedding_ip 
        ON tracks 
        USING hnsw (embedding vector_ip_ops)
    """)
    
    # embedding HNSW (L2 - 유클리디안 거리)
    op.execute("""
        CREATE INDEX ix_tracks_embedding_l2 
        ON tracks 
        USING hnsw (embedding vector_l2_ops)
    """)
    
    # popularity 인덱스
    op.create_index('ix_tracks_popularity', 'tracks', ['popularity'])
    
    # =====================
    # playlists 테이블
    # =====================
    # user_id 인덱스
    op.create_index('ix_playlists_user_id', 'playlists', ['user_id'])
    
    # user_id + created_at 복합 인덱스
    op.create_index('ix_playlists_user_id_created_at', 'playlists', ['user_id', 'created_at'])
    
    # =====================
    # playlist_tracks 테이블
    # =====================
    # playlist_id 인덱스
    op.create_index('ix_playlist_tracks_playlist_id', 'playlist_tracks', ['playlist_id'])
    
    # playlist_id + position UNIQUE
    op.create_unique_constraint(
        'uq_playlist_tracks_playlist_id_position', 
        'playlist_tracks', 
        ['playlist_id', 'position']
    )
    
    # =====================
    # user_preferences 테이블
    # =====================
    # user_id 인덱스
    op.create_index('ix_user_preferences_user_id', 'user_preferences', ['user_id'])
    
    # user_id + created_at 복합 인덱스
    op.create_index(
        'ix_user_preferences_user_id_created_at', 
        'user_preferences', 
        ['user_id', 'created_at']
    )
    
    # =====================
    # track_interactions 테이블
    # =====================
    # created_at 인덱스
    op.create_index('ix_track_interactions_created_at', 'track_interactions', ['created_at'])
    
    # user_id + created_at 복합 인덱스 (user_id 단일 조회도 커버)
    op.create_index(
        'ix_track_interactions_user_id_created_at', 
        'track_interactions', 
        ['user_id', 'created_at']
    )
    
    # track_id + created_at 복합 인덱스 (track_id 단일 조회도 커버)
    op.create_index(
        'ix_track_interactions_track_id_created_at', 
        'track_interactions', 
        ['track_id', 'created_at']
    )


def downgrade() -> None:
    # track_interactions
    op.drop_index('ix_track_interactions_track_id_created_at', 'track_interactions')
    op.drop_index('ix_track_interactions_user_id_created_at', 'track_interactions')
    op.drop_index('ix_track_interactions_created_at', 'track_interactions')
    
    # user_preferences
    op.drop_index('ix_user_preferences_user_id_created_at', 'user_preferences')
    op.drop_index('ix_user_preferences_user_id', 'user_preferences')
    
    # playlist_tracks
    op.drop_constraint('uq_playlist_tracks_playlist_id_position', 'playlist_tracks', type_='unique')
    op.drop_index('ix_playlist_tracks_playlist_id', 'playlist_tracks')
    
    # playlists
    op.drop_index('ix_playlists_user_id_created_at', 'playlists')
    op.drop_index('ix_playlists_user_id', 'playlists')
    
    # tracks
    op.drop_index('ix_tracks_popularity', 'tracks')
    op.execute('DROP INDEX ix_tracks_embedding_l2')
    op.execute('DROP INDEX ix_tracks_embedding_ip')
    op.execute('DROP INDEX ix_tracks_norm_features_l2')
    
    # users
    op.drop_constraint('uq_users_spotify_user_id', 'users', type_='unique')
    op.drop_constraint('uq_users_guest_id', 'users', type_='unique')
