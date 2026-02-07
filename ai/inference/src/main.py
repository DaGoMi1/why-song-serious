import uvicorn
from fastapi import FastAPI
from src.core.recommender import RecommenderEngine
import yaml
from contextlib import asynccontextmanager

# 서버 시작 시 엔진 로드 (한 번만)
with open("src/config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application started")
    yield
    print("Shutting down...")

app = FastAPI(
    title="Why Song Serious AI API",
    version="0.1.0",
    lifespan=lifespan,
    root_path="/ai"
)

# 추천 엔진 선언
engine = RecommenderEngine(config)

# API 라우터 연결
from src.api.recommend import router as rec_router
app.include_router(rec_router, prefix="/ai")

@app.get("/health")
async def health_check():
    return {"status": "ai healthy"}