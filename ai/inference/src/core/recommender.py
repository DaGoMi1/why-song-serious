import os
import joblib
import torch
import numpy as np
import pandas as pd
from src.models.deepfm import DeepFM
from src.core.retrieval import SongRetriever
from src.core.ranker import SongRanker

class RecommenderEngine:
    def __init__(self, config):
        print("[Engine] 초기화 시작 - 서버 시작시 한번만 실행될 것임")
        self.config = config
        self.base_path = config['paths']
        self.assets_path = self.base_path['assets_path']
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print("[Engine] 메타데이터 로딩 중...")
        # 메타데이터 및 에셋 로드
        self.item_meta = pd.read_pickle(os.path.join(self.assets_path, self.base_path['item_meta_deepfm']))
        self.label_encoders = joblib.load(os.path.join(self.assets_path, self.base_path['encoders']))
        print(f"메타데이터 로드 완료 (Device: {self.device})")

        print("[Engine] DeepFM 모델 빌드 및 가중치 로드 중...")
        # DeepFM 모델 빌드 및 가중치 로드
        feature_dims = {col: len(le.classes_) for col, le in self.label_encoders.items()}
        hidden_layers = self.config['model']['hidden_layers']
        dropout = self.config['model']['dropout']

        self.model = DeepFM(
            feature_dims=feature_dims, 
            embedding_dim=self.config['model']['embedding_dim'],
            hidden_layers=hidden_layers,
            dropout=dropout
        )
        
        # 가중치(.pt) 로드
        model_path = os.path.join(self.assets_path, self.base_path['model_path'])
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()
        print("모델 로드 완료")
        
        print("[Engine] SongRetriever(FAISS) 초기화 중...")
        # 리트리버 초기화
        self.retriever = SongRetriever(config=self.config)
        print("리트리버 준비 완료")

        print("[Engine] SongRanker 초기화 중...")
        # 랭커 초기화
        self.ranker = SongRanker(
            model=self.model, 
            label_encoders=self.label_encoders,
            item_meta=self.item_meta,
            config=self.config,
            device=self.device
        )
        print("[Engine] 초기화 완료")

    def recommend(self, seed_song_ids, pid=8):
        """Faiss로 후보군 뽑고 DeepFM으로 리랭킹"""

        candidates, best_pid = self.retriever.retrieve(seed_ids=seed_song_ids)
        ranked_df = self.ranker.rank(candidates, best_pid)
    
        return ranked_df