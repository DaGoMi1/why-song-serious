import os
import json
import joblib
import pandas as pd
from annoy import AnnoyIndex

class SongAnnoySearcher:
    def __init__(self, config):
        self.config = config
        self.assets_path = config['paths']['assets_path']
        
        # Annoy 설정 로드
        self.annoy_dim = self.config['annoy']['dim']
        self.audio_cols = self.config['annoy']['audio_cols']
        self.k = self.config['recommendation']['slider_top_k']

        # 에셋 로드 (인덱스, 스케일러, ID 맵)
        self.index = AnnoyIndex(self.annoy_dim, 'euclidean')
        self.index.load(os.path.join(self.assets_path, 'annoy/music_annoy.ann'))
        
        self.scaler = joblib.load(os.path.join(self.assets_path, 'annoy/scaler_annoy.pkl'))
        
        with open(os.path.join(self.assets_path, 'annoy/id_mapping_annoy.json'), 'r') as f:
            self.id_map = json.load(f)
            
        # 메타데이터 로드 (결과 반환용)
        self.item_meta = pd.read_csv(os.path.join(self.assets_path, config['paths']['item_metadata']))

    def search(self, user_input_dict):
        """
        슬라이더 값(dict)을 받아 가장 유사한 곡들을 반환
        """
        # 입력 데이터 순서 맞추기 및 데이터프레임 변환
        input_values = [user_input_dict[col] for col in self.audio_cols]
        input_df = pd.DataFrame([input_values], columns=self.audio_cols)
        
        # 스케일링 및 검색
        scaled_vector = self.scaler.transform(input_df)[0]
        indices = self.index.get_nns_by_vector(scaled_vector, self.k)
        
        # ID 변환 및 메타데이터 필터링
        res_ids = [self.id_map[str(idx)] for idx in indices]
        return self.item_meta[self.item_meta['id'].isin(res_ids)]