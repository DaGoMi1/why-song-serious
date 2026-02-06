from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class RecommendRequest(BaseModel):
    seed_song_ids: List[str]
    pid: int = 824067

@router.post("/recommend")
async def get_recommendation(request: RecommendRequest):
    try:
        from src.main import engine  # 전역 엔진 가져오기
        
        # 엔진 실행
        results = engine.recommend(
            seed_song_ids=request.seed_song_ids, 
            pid=request.pid
        )
        
        # DataFrame을 JSON(List of Dict)으로 변환하여 반환
        return {
            "status": "success",
            "data": results.to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))