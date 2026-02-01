from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import os

app=FastAPI()

origins=[
    "http://localhost:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def load_json(filename):
    current_dir=os.path.dirname(os.path.abspath(__file__))
    file_path=os.path.join(current_dir, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
    
@app.get("/")
def read_root():
    return {"message": "Backend is Running"}

@app.get("/api/tracks")
def get_tracks():
    data=load_json('tracks.json')
    return data

@app.get("/api/cluster")
def get_cluster_data():
    data=load_json('clustered_data.json')
    return data