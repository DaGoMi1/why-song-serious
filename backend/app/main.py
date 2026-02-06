from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.auth.router import router as auth_router

from app.domain import models

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application started")
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

from app.domain.track.router import router as track_router
app.include_router(track_router)

from app.domain.preference.router import router as preference_router
app.include_router(preference_router)

from app.domain.recommendation.router import router as recommendation_router
app.include_router(recommendation_router)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
