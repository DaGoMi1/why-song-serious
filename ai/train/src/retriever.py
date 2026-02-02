import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

class Retriever:
    def __init__(self, audio_cols, retriever_k=500, label_encoders=None):
        self.audio_cols = audio_cols
        self.retriever_k = retriever_k
        self.label_encoders = label_encoders
        self.scaler = MinMaxScaler()
        self.index = None
        self.filtered_df = None

    def prepare_data(self, file_path):
        # 중복 제거 및 데이터 정제
        df = pd.read_csv(file_path)
        df = df.drop(['pid'], axis=1)
        self.filtered_df = df.drop_duplicates('id', keep='first').reset_index(drop=True)
        
        for col, encoder in self.label_encoders.items():
            if col in self.filtered_df.columns:
                # transform을 사용하여 학습 때 구축한 사전을 그대로 적용
                self.filtered_df[col] = encoder.transform(self.filtered_df[col].astype(str))
        
        # 스케일링
        audio_data = self.filtered_df[self.audio_cols].values
        scaled_data = self.scaler.fit_transform(audio_data)
        
        # Faiss 인덱스 구축
        dim = len(self.audio_cols)
        self.index = faiss.IndexFlatL2(dim)  # Annoy의 'euclidean'과 동일
        
        # 메모리를 연속적으로 재배치하는 함수
        data_to_add = np.ascontiguousarray(scaled_data.astype('float32'))
        self.index.add(data_to_add)
        
        print(f"인덱스 구축 완료: {self.index.ntotal}곡.")

    def retrieve(self, song_ids):
        seed_songs = self.filtered_df[self.filtered_df['id'].isin(song_ids)]
        seed_features = seed_songs[self.audio_cols].values.astype('float32')
        scaled_seeds = self.scaler.transform(seed_features)
        
        # 평균 벡터 (전체 취향의 중심)
        mean_vector = np.mean(scaled_seeds, axis=0, keepdims=True)
        
        # 개별 곡 벡터 + 평균 벡터 합치기
        query_vectors = np.vstack([mean_vector, scaled_seeds])
        query_vectors = np.ascontiguousarray(query_vectors.astype('float32'))

        # 검색
        distances, indices = self.index.search(query_vectors, self.retriever_k)
        
        # 중복 제거 및 순서 보존
        flat_indices = indices.flatten()
        unique_indices = list(dict.fromkeys(flat_indices))
        if -1 in unique_indices: unique_indices.remove(-1)
        
        candidates = self.filtered_df.iloc[unique_indices].copy()
        candidates = candidates[~candidates['id'].isin(song_ids)]
        
        return candidates.head(self.retriever_k)