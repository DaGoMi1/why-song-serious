from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os

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

@app.post("/api/recommend")
def get_tracks():
    data=load_json('tracks_recommend.json')
    explanation_data = load_json('playlist_explanation.json')
    return {"tracks": data, "explanation": explanation_data}

@app.get("/api/cluster")
def get_cluster_data():
    data=load_json('clustered_data.json')
    return data

@app.post("/api/search")
def recommend_tracks(request: RetrievalRequest):
    print("Received request:", request)
    print("preference:", request.preferences)
    data=load_json('tracks_retrieval.json')
    
    recommended_tracks=data.copy()
    return recommended_tracks[:request.limit]  