import faiss
import joblib
import json
import os
import numpy as np
import pandas as pd

class SongRetriever:
    def __init__(self, config):
        self.config = config
        self.base_path = config['paths']
        self.assets_path = self.base_path['assets_path']
        
        # Faiss 인덱스 및 스케일러 로드
        self.index = faiss.read_index(os.path.join(self.assets_path, self.base_path['faiss_index']))
        self.scaler = joblib.load(os.path.join(self.assets_path, self.base_path['scaler']))
            
        # 메타데이터 로드 (추후 리랭커 전달용)
        self.item_meta = pd.read_pickle(os.path.join(self.assets_path, self.base_path['item_meta_faiss']))
        self.item_inter = pd.read_pickle(os.path.join(self.assets_path, self.base_path['item_inter']))
        
        # 오디오 피처 정의 (학습 시와 동일한 순서여야 함)
        self.audio_cols = config['model']['audio_cols']

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
        scaled_seeds = self.scaler.transform(seed_features_df.values)
        
        # 평균 벡터 (전체 취향의 중심)
        mean_vector = np.mean(scaled_seeds, axis=0, keepdims=True)
        
        # 개별 곡 벡터 + 평균 벡터 합치기
        # 중심점과 개별점을 모두 쿼리로 사용합니다.
        query_vectors = np.vstack([mean_vector, scaled_seeds])
        query_vectors = np.ascontiguousarray(query_vectors.astype('float32'))
        
        # 모든 쿼리 벡터(평균 + 개별곡)로 검색
        # 각 포인트마다 k개씩 찾으므로 총 (n+1)*k 후보가 생김
        distances, indices = self.index.search(query_vectors, self.k)

        # 중복 제거 및 유효한 인덱스 추출
        flat_indices = indices.flatten()
        unique_indices = []
        seen = set()
        for idx in flat_indices:
            # -1은 Faiss에서 결과가 없을 때 채우는 값임
            if idx != -1 and idx not in seen:
                unique_indices.append(idx)
                seen.add(idx)

        # 행 번호(indices)를 이용해 원본 문자열 ID 추출
        # iloc으로 접근해서 'id' 컬럼(문자열)만 가져옵니다.
        candidate_ids = self.item_meta.iloc[unique_indices]['id'].tolist()

        # 입력으로 넣었던 곡(seed_ids)은 후보에서 제외
        candidate_ids = [cid for cid in candidate_ids if cid not in seed_ids]

        best_pid = self.find_best_pid(seed_ids)

        # 최종 설정된 top_k 개수만큼만 반환
        return candidate_ids[:self.k], best_pid
    
    def find_best_pid(self, seed_ids):
        # 시드 곡들이 포함된 행들만 필터링 (item_inter 사용)
        relevant_playlists = self.item_inter[self.item_inter['id'].isin(seed_ids)]
        
        if relevant_playlists.empty:
            # 만약 학습 데이터에 시드 곡이 하나도 없다면 가장 인기가 많은 PID
            # 가장 많은 곡을 가진 PID 824067번
            return 824067

        # 시드 곡이 가장 많이 포함된(겹치는) PID 찾기
        # 'pid' 컬럼으로 그룹화하여 개수를 세고, 가장 빈도수가 높은 index(pid)를 가져옴
        best_pid = relevant_playlists.groupby('pid').size().idxmax()
        
        return int(best_pid)