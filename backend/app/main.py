from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.auth.router import router as auth_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.database import engine, Base
    from app.domain.models import User, AuthType, Track, Playlist, PlaylistTrack, UserPreference, TrackInteraction  # 모든 모델 import
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created")
    yield
    print("Shutting down...")


app = FastAPI(
    title="Why Song Serious",
    description="음악 취향 기반 탐색 및 시각화 서비스",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/api"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)



@app.get("/health")
async def health_check():
    return {"status": "healthy"}
