import pandas as pd
import numpy as np
import torch
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch.utils.data import DataLoader as PyTorchDataLoader, TensorDataset
from scipy.sparse import csr_matrix
import ast


class EASEDataLoader:
    def __init__(self, file_path, device, random_state=42):
        self.df = pd.read_csv(file_path)
        self.label_encoders = {}
        self.device = device
        self.random_state = random_state

    def preprocess(self):

        df = self.df.copy(deep=True)

        p_le = LabelEncoder()
        t_le = LabelEncoder()

        df['pid'] = p_le.fit_transform(df['pid'])
        df['id'] = t_le.fit_transform(df['id'])

        self.label_encoders = {
            'playlists' : p_le,
            'id' : t_le
        }
        
        num_playlists = df['pid'].nunique()
        num_tracks = df['id'].nunique()

        rows = df['pid'].values
        cols = df['id'].values
        data = np.ones(len(df))

        matrix = csr_matrix((data, (rows, cols)), shape=(num_playlists, num_tracks)).toarray()

        return matrix
    
    def split_data(self, matrix, test_size=0.1, hidden_count=3):
        train, test = train_test_split(matrix, test_size=test_size, random_state=self.random_state)
        
        train = torch.FloatTensor(train).to(self.device)

        test_X = test.copy()
        test_y = np.zeros_like(test)

        rng = np.random.default_rng(self.random_state)

        for i in range(len(test)):
            # 해당 유저가 소비한 아이템 인덱스들
            interacted_items = np.where(test[i] > 0)[0]
            
            if len(interacted_items) > hidden_count:
                # 숨길 아이템 인덱스 선택
                hidden_indices = rng.choice(interacted_items, size=hidden_count, replace=False)
                
                test_X[i, hidden_indices] = 0  # 입력에서 지움 (문제)
                test_y[i, hidden_indices] = 1 # 정답지에 기록 (정답)

        # 4. Test 텐서 변환
        test_input = torch.FloatTensor(test_X).to(self.device)
        test_label = torch.FloatTensor(test_y).to(self.device)

        return train, test_input, test_label
