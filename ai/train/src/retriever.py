import faiss
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import faiss

class Retriever:
    def __init__(self, audio_cols, retriever_k=500, loader=None):
        self.audio_cols = audio_cols
        self.retriever_k = retriever_k
        self.label_encoders = loader.label_encoders
        self.bin_edges = loader.bin_edges
        self.scaler = MinMaxScaler()
        self.index = None
        self.item_meta = pd.read_csv("./data/item_meta.csv")
        self.item_meta_enc = self.item_meta.drop(audio_cols, axis=1)

    def prepare_data(self, file_path):
        print("item_meta 데이터 사전 인코딩 중...")
        
        # 연속형 컬럼 구간화(Binning) 미리 처리
        for col in self.audio_cols:
            bin_name = f"{col}_bin"
            self.item_meta_enc[bin_name] = pd.cut(
                self.item_meta[col], 
                bins=self.bin_edges[col], 
                labels=False, 
                include_lowest=True
            ).astype(int)

        # 범주형 인코딩 미리 처리
        for col, encoder in self.label_encoders.items():
            if col in self.item_meta_enc.columns:
                # 미리 한 번에 전체 데이터를 변환
                self.item_meta_enc[col] = encoder.transform(
                    self.item_meta_enc[col].astype(str).map(
                        lambda x: x if x in encoder.classes_ else encoder.classes_[0]
                    )
                )
        print("사전 인코딩 완료!")

        print(f"곡 길이 {len(self.item_meta)}")

        # 스케일링
        audio_data = self.item_meta[self.audio_cols].values
        scaled_data = self.scaler.fit_transform(audio_data)
        
        # Faiss 인덱스 구축
        dim = len(self.audio_cols)
        self.index = faiss.IndexFlatL2(dim)  # Annoy의 'euclidean'과 동일
        
        # float32 변환 후 메모리를 연속적으로 재배치합니다.
        data_to_add = np.ascontiguousarray(scaled_data.astype('float32'))
        self.index.add(data_to_add)
        
        print(f"인덱스 구축 완료: {self.index.ntotal}곡.")

    def retrieve(self, song_ids):
        id_encoder = self.label_encoders['id'] 
        decoded_ids = id_encoder.inverse_transform(song_ids)

        seed_songs = self.item_meta[self.item_meta['id'].isin(decoded_ids)]
        
        seed_features = seed_songs[self.audio_cols].values.astype('float32')
        scaled_seeds = self.scaler.transform(seed_features)
        
        # 평균 벡터 (전체 취향의 중심)
        mean_vector = np.mean(scaled_seeds, axis=0, keepdims=True)
        
        # 개별 곡 벡터 + 평균 벡터 합치기
        # 중심점과 개별점을 모두 쿼리로 사용
        query_vectors = np.vstack([mean_vector, scaled_seeds])
        query_vectors = np.ascontiguousarray(query_vectors.astype('float32'))

        # 검색
        distances, indices = self.index.search(query_vectors, self.retriever_k)
        
        # 중복 제거 및 순서 보존
        flat_indices = indices.flatten()
        unique_indices = list(dict.fromkeys(flat_indices))
        if -1 in unique_indices: unique_indices.remove(-1)
        
        # 미리 인코딩된 item_meta_enc에서 데이터를 가져옴
        candidates = self.item_meta_enc.iloc[unique_indices].copy()
        candidates = candidates[~candidates['id'].isin(song_ids)]
        
        encoded_pid = self.find_best_pid(song_ids)

        if 'pid' in candidates.columns:
            candidates = candidates.drop(columns=['pid'])
        
        # 맨 앞에 인코딩된 pid 정수값 삽입
        candidates.insert(0, 'pid', encoded_pid)
        
        # 최종 리턴 
        return candidates.head(self.retriever_k)
    
    def find_best_pid(self, song_ids):
        """시드 곡들과 유사한 PID를 찾아 '인코딩된 정수'로 반환"""
        # 입력된 인코딩 ID -> 원본 ID로 디코딩
        decoded_ids = self.label_encoders['id'].inverse_transform(song_ids)
        seed_songs = self.item_meta[self.item_meta['id'].isin(decoded_ids)]
        
        if seed_songs.empty:
            best_pid_raw = 824067
        else:
            # 거리 기반 최적 PID(원본 번호) 탐색
            seed_mean = seed_songs[self.audio_cols].mean().values.reshape(1, -1)
            scaled_seed_mean = self.scaler.transform(seed_mean).astype('float32')
            _, indices = self.pid_index.search(np.ascontiguousarray(scaled_seed_mean), 1)
            
            # 검색 결과가 있으면 해당 PID 추출, 없으면 기본값
            best_pid_raw = self.pid_list[indices[0][0]] if indices[0][0] != -1 else 824067

        # 찾은 원본 PID를 레이블 인코더로 인코딩 (문자열 변환 후 인코딩)
        pid_encoder = self.label_encoders['pid']
        pid_str = str(best_pid_raw)
        
        if pid_str in pid_encoder.classes_:
            encoded_pid = pid_encoder.transform([pid_str])[0]
        else:
            encoded_pid = 0 
            
        return encoded_pid