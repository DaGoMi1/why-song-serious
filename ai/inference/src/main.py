import uvicorn
from fastapi import FastAPI
from src.core.recommender import RecommenderEngine
import yaml

app = FastAPI(title="Music Recommendation API")

# 서버 시작 시 엔진 로드 (한 번만)
with open("src/config/config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 추천 엔진 선언
engine = RecommenderEngine(config)

# API 라우터 연결
from src.api.recommend import router as rec_router
app.include_router(rec_router, prefix="/ai")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)