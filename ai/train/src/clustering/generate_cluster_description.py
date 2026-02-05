import os
import json
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import requests
from pathlib import Path
import ast
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import login

from prompt import build_prompt

# huggingface 로그인
HF_TOKEN = os.environ.get("HUGGINGFACE_TOKEN")

login(token=HF_TOKEN)

# 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent  #프로젝트 root dir
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"

# Gemma 호출 함수
def call_gemma(prompt, max_new_tokens=150):
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024
    ).to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,          
            temperature=0.7,
            top_p=0.9,
            eos_token_id=tokenizer.eos_token_id
        )

    decoded = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[-1]:],
        skip_special_tokens=True
    )

    return decoded.strip()

# 대표 features 및 방향성 함수
def top_features_with_directions(cluster_z, top_k=3):
    result = {}
    for cid, row in cluster_z.iterrows():
        top = row.sort_values(key=lambda x: x.abs(), ascending=False).head(top_k)
        result[cid] = {
            feat: "↑" if val > 0 else "↓"
            for feat, val in top.items()
        }
    return result

# 대표곡 선정 함수 - embedding centroid 
def select_representative_tracks(item_embedding, cluster_df, track_df, top_k=10):
    # embedding + cluster 정보 결합 
    embedding_df = pd.DataFrame(item_embedding)
    embedding_df["cluster_id"] = cluster_df["cluster_number"].values
    embedding_df["track_id"] = cluster_df["id"].values

    # track metadata
    track_meta = track_df.set_index("id")[["name", "artists"]]

    representative_tracks = {}

    for cid in embedding_df["cluster_id"].unique():
        cluster_points = embedding_df[embedding_df["cluster_id"] == cid]
        vectors = cluster_points.iloc[:, :-2].values

        center = vectors.mean(axis=0, keepdims=True)
        dists = euclidean_distances(vectors, center).flatten()

        top_idx = np.argsort(dists)[:top_k]
        selected = cluster_points.iloc[top_idx]["track_id"]

        tracks = []
        for tid in selected:
            row = track_meta.loc[tid]
            
            # artists 문자열 안전 처리 - 형식 처리
            artists = row["artists"]
            if isinstance(artists, str) and artists.startswith("["):
                artist_str = ", ".join(ast.literal_eval(artists))
            else:
                artist_str = str(artists)

            tracks.append((row["name"], artist_str))
    
        representative_tracks[cid] = tracks

    return representative_tracks


# 데이터 로드
item_label = pd.read_csv(DATA_DIR / "item_label_mapping.csv")
item_embedding = np.load(DATA_DIR / "item_embeddings.npy")

with open(DATA_DIR / "for_cluster.json", "r") as f:
    cluster_info = json.load(f)

cluster_df = pd.DataFrame(cluster_info)
# columns: id, emb1, emb2, cluster_number

merge_df = pd.read_csv(DATA_DIR / "add_feature_v2.csv")

# 곡 정보만 유지
track_df = pd.DataFrame(
    merge_df
    .drop_duplicates(subset="id")
    .drop(columns=["pid"])
    .reset_index(drop=True)
)

# cluster_id 매핑
cluster_uri_df = cluster_df[["id","cluster_number"]].rename(
    columns={"id": "uri", "cluster_number":"cluster_id"}
)

cluster_feature_df = track_df.merge(
    cluster_uri_df,
    left_on="id",
    right_on="uri",
    how="inner"
)

# 클러스터 별 feature 값 계산 (z-score)

## 계산할 feature
features = [
    "energy", "valence", "danceability",
    "acousticness", "instrumentalness",
    "speechiness", "tempo", "popularity"
]

cluster_mean = cluster_feature_df.groupby("cluster_id")[features].mean()
global_mean = cluster_feature_df[features].mean()
global_std = cluster_feature_df[features].std()

cluster_z = (cluster_mean - global_mean) / global_std

## 클러스터 별 대표 특성 및 방향성 
cluster_feature_top = top_features_with_directions(cluster_z)

# 대표곡 선정 (embedding centroid)
representative_tracks = select_representative_tracks(item_embedding,cluster_df,track_df)

# Gemma 로드
MODEL_NAME = "google/gemma-3-4b-it"
# MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"   # Qwen 모델 사용 시

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    device_map="auto"
)

model.eval()

# LLM 설명 생성
cluster_descriptions = {}

for cid in representative_tracks:
    prompt = build_prompt(
        representative_tracks[cid],
        cluster_feature_top.get(cid, {})
    )

    response = call_gemma(prompt)

    cluster_descriptions[cid] = response.strip()

print("sample keys:", list(cluster_descriptions.keys())[:5])

# json 파일로 저장
tmp_path = OUTPUT_DIR / "cluster_description.tmp.json"
final_path = OUTPUT_DIR / "cluster_description.json"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_DIR / "cluster_description.json", "w", encoding="utf-8") as f:
    json.dump(cluster_descriptions, f, ensure_ascii=False, indent=2)
    f.flush()
    os.fsync(f.fileno())

tmp_path.replace(final_path)
print("cluster_description.json 생성 완료")
    