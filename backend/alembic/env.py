import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy import engine_from_config

from alembic import context

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import get_settings
from app.database import Base

# 모든 모델 import (autogenerate가 감지할 수 있도록)
from app.domain.models import (
    User,
    Track,
    Playlist,
    PlaylistTrack,
    UserPreference,
    TrackInteraction,
)

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 메타데이터 설정 (autogenerate용)
target_metadata = Base.metadata


def get_sync_database_url() -> str:
    """
    async URL을 sync URL로 변환
    postgresql+asyncpg:// -> postgresql://
    """
    settings = get_settings()
    url = settings.database_url
    
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    
    return url


def run_migrations_offline() -> None:
    """
    'Offline' 모드로 마이그레이션 실행
    SQL 스크립트만 생성하고 실제 DB 연결은 하지 않음
    """
    url = get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    'Online' 모드로 마이그레이션 실행
    실제 DB에 연결하여 마이그레이션 적용
    """
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_sync_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
