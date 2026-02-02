import faiss
import joblib
import json
import os
import numpy as np
import pandas as pd

class SongRetriever:
    def __init__(self, config):
        self.config = config
        self.assets_path = config['paths']['assets_path']
        
        # Faiss 인덱스 및 스케일러 로드
        self.index = faiss.read_index(os.path.join(self.assets_path, "faiss/vector_db.index"))
        self.scaler = joblib.load(os.path.join(self.assets_path, "faiss/scaler_faiss.pkl"))
        
        # ID 매핑 로드
        with open(os.path.join(self.assets_path, "faiss/id_mapping_faiss.json"), "r") as f:
            self.id_map = json.load(f)
            
        # 메타데이터 로드 (추후 리랭커 전달용)
        self.item_meta = pd.read_csv(os.path.join(self.assets_path, self.config['paths']['item_metadata']))
        
        # 오디오 피처 정의 (학습 시와 동일한 순서여야 함)
        self.audio_cols = ['acousticness', 'valence', 'energy', 'danceability', 'instrumentalness', 'loudness', 'speechiness', 'tempo', 'popularity']

        self.k = self.config['recommendation']['retrieval_top_k']

    def retrieve(self, seed_ids):
        """플레이리스트 내 곡 ID들을 기반으로 후보군 추출"""
            
        # seed_ids에 해당하는 곡들의 피처 추출
        seed_songs = self.item_meta[self.item_meta['id'].isin(seed_ids)]
        if seed_songs.empty:
            raise ValueError("입력값이 비어있습니다.")

        # 스케일링 및 쿼리 벡터 생성 (평균 벡터 사용)
        seed_features = seed_songs[self.audio_cols].values
        seed_features_df = pd.DataFrame(seed_features, columns=self.audio_cols)
        scaled_seeds = self.scaler.transform(seed_features_df)
        mean_vector = np.mean(scaled_seeds, axis=0, keepdims=True).astype('float32')
        
        # Faiss 검색
        distances, indices = self.index.search(mean_vector, self.k)
        
        # 인덱스를 곡 ID로 변환
        candidate_ids = [self.id_map[str(idx)] for idx in indices[0] if idx != -1]
        
        # 원래 있던 곡(seed_ids)은 제외하고 메타데이터 반환
        candidates = self.item_meta[self.item_meta['id'].isin(candidate_ids)]
        candidates = candidates[~candidates['id'].isin(seed_ids)]
        
        return candidates