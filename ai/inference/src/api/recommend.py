from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from src.main import engine

router = APIRouter()

class RecommendRequest(BaseModel):
    model_type: str
    seed_song_ids: List[str]

@router.post("/recommendations/ai")
async def get_recommendation(request: RecommendRequest):
    mt = request.model_type.lower()
    
    try:
        if mt == "deepfm":
            results = engine.recommend(
                seed_song_ids=request.seed_song_ids, 
                pid=engine.config['data']['unseen_pid']
            )
        elif mt == "ease":
            raise HTTPException(status_code=501, detail="EASE 모델은 현재 준비 중입니다.")
            
        elif mt == 'lightgcn':
            raise HTTPException(status_code=501, detail="LightGCN 모델은 현재 준비 중입니다.")
            
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 추천 모델입니다: {mt}")

        return {
            "status": "success",
            "model_type": mt,
            "data": results.to_dict(orient="records")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation Error: {str(e)}")