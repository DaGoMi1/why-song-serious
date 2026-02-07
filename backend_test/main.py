from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import uuid

app=FastAPI()

origins=[
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:4173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class PreferenceFeatures(BaseModel):
    energy: float
    valence: float
    danceability: float
    acousticness: float
    loudness: float
    tempo: float
    
class RetrievalRequest(BaseModel):
    preferences: PreferenceFeatures
    limit: int = 20

def load_json(filename):
    current_dir=os.path.dirname(os.path.abspath(__file__))
    file_path=os.path.join(current_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
@app.get("/")
def read_root():
    return {"message": "Backend is Running"}

@app.post("/api/recommendations")
def get_tracks():
    data=load_json('tracks_recommend.json')
    explanation_data = load_json('playlist_explanation.json')
    return {"tracks": data, "description": explanation_data}

@app.get("/api/cluster")
def get_cluster_data():
    data=load_json('clustered_data.json')
    return data

@app.post("/api/tracks/search")
def recommend_tracks(request: RetrievalRequest):
    # DB에 preference 저장
    # 일단 임시 아이디 사용
    generated_preference_id = 123
    print("Received request:", request)
    print("preference:", request.preferences)
    data=load_json('tracks_retrieval.json')
    
    recommended_tracks=data.copy()

    response= {
        "preference_id": generated_preference_id, 
        "tracks": recommended_tracks
    }

    return response

class Token(BaseModel):
    access_token: str
    token_type: str

@app.post("/api/auth/guest", response_model=Token)
async def login_as_guest():
    guest_token = f"guest_{uuid.uuid4()}"
    
    print(f"✅ 새로운 게스트 토큰 발급됨: {guest_token}")
    return {
        "access_token": guest_token,
        "token_type": "bearer"
    }
