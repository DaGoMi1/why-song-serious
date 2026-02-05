import os
import joblib
import torch
import numpy as np
import pandas as pd
from models.deepfm import DeepFM
from core.retrieval import SongRetriever
from core.ranker import SongRanker

class RecommenderEngine:
    def __init__(self, config):
        self.config = config
        self.assets_path = config['paths']['assets_path']
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        # 메타데이터 및 에셋 로드
        self.item_meta = pd.read_csv(os.path.join(self.assets_path, self.config['paths']['item_metadata']))
        self.label_encoders = joblib.load(os.path.join(self.assets_path, 'deepfm/label_encoders.pkl'))
        
        # DeepFM 모델 빌드 및 가중치 로드
        feature_dims = {col: len(le.classes_) for col, le in self.label_encoders.items()}
        continuous_cols = self.config['model']['continuous_features']
        hidden_layers = self.config['model']['hidden_layers']
        dropout = self.config['model']['dropout']
        
        self.model = DeepFM(
            feature_dims=feature_dims, 
            embedding_dim=self.config['model']['embedding_dim'],
            continuous_cols=continuous_cols,
            hidden_layers=hidden_layers,
            dropout=dropout
        )
        
        # 가중치(.pt) 로드
        model_path = os.path.join(self.assets_path, 'deepfm/prototype_v1_best_model.pt')
        self.model.load_state_dict(torch.load(model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        # 리트리버 초기화
        self.retriever = SongRetriever(config=self.config)

        # 랭커 초기화
        self.ranker = SongRanker(
            model=self.model, 
            label_encoders=self.label_encoders,
            config=self.config,
            device=self.device
        )

    def recommend(self, seed_song_ids, pid=824067):
        """Faiss로 후보군 뽑고 DeepFM으로 리랭킹"""

        candidates = self.retriever.retrieve(seed_ids=seed_song_ids)
        ranked_df = self.ranker.rank(candidates, pid)
    
        return ranked_df