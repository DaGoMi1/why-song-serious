import pandas as pd
import numpy as np
import torch
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from torch.utils.data import DataLoader as PyTorchDataLoader, TensorDataset
import ast

class DeepFMDataLoader:
    def __init__(self, file_path, cat_cols, cont_cols, random_state=42):
        self.df = pd.read_csv(file_path)
        self.cat_cols = cat_cols
        self.cont_cols = cont_cols
        self.label_encoders = {}
        self.scaler = StandardScaler()
        self.random_state = random_state

    def split_data(self, test_size=0.1, hidden_count=3):
        """
        9:1로 train/test 셋을 나누고 
        각각의 pid별로 3개의 아이템을 검증 및 메트릭 계산용으로 분리 시키는 작업
        """
        # pid 기준으로 train/test 셋 분할
        unique_pids = self.df['pid'].unique()
        train_pids, test_pids = train_test_split(unique_pids, test_size=test_size, random_state=self.random_state)

        train_df = self.df[self.df['pid'].isin(train_pids)].copy()
        test_df = self.df[self.df['pid'].isin(test_pids)].copy()

        # 입력 받은 hidden_count개의 아이템을 분리 시키는 함수
        def leave_items_out(group, n):
            if len(group) <= n:
                raise ValueError(f"n이 pid내 아이템 개수보다 크거나 같음. 데이터셋 구조 다시 확인 필요")
            
            hidden = group.sample(n=n, random_state=self.random_state)

            input_data = group.drop(hidden.index)
            return input_data, hidden
        
        train_list = []
        valid_list = []
        test_input_list = []
        test_label_list = []

        # leave_items_out 함수 이용해서 데이터 분리 및 저장
        for pid, group in train_df.groupby('pid'):
            input, label = leave_items_out(group, hidden_count)
            train_list.append(input)
            valid_list.append(label)

        for pid, group in test_df.groupby('pid'):
            input, label = leave_items_out(group, hidden_count)
            test_input_list.append(input)
            test_label_list.append(label)

        train_data = pd.concat(train_list)
        valid_data = pd.concat(valid_list)
        test_input = pd.concat(test_input_list)
        test_label = pd.concat(test_label_list)

        # 최종 반환
        return train_data, valid_data, test_input, test_label
    
    def preprocess(self):
        """
        범주형 데이터 라벨 인코딩
        수치형 데이터 정규화
        feature_dims 계산
        """
        if 'popularity' in self.df.columns:
            # 5개 구간으로 나누어 'pop_grade'라는 새로운 범주형 피쳐 생성
            self.df['pop_grade'] = pd.cut(self.df['popularity'], 
                                          bins=[0, 40, 60, 73, 80, 101], 
                                          labels=[0, 1, 2, 3, 4], 
                                          right=False).astype(int)
            
            # 범주형 피쳐 리스트에 추가
            if 'pop_grade' not in self.cat_cols:
                self.cat_cols.append('pop_grade')
        
        # 범주형 데이터 라벨 인코딩
        for col in self.cat_cols:
            le = LabelEncoder()
            self.df[col] = le.fit_transform(self.df[col])
            self.label_encoders[col] = le
        
        # 수치형 데이터 정규화
        if self.cont_cols:
            self.df[self.cont_cols] = self.scaler.fit_transform(self.df[self.cont_cols])

        # feature_dims 계산
        feature_dims = {col: self.df[col].nunique() for col in self.cat_cols}

        print(f"전체 데이터 pid 수: {feature_dims.get(self.cat_cols[0])}")
        print(f"전체 데이터 id 수: {feature_dims.get(self.cat_cols[1])}")

        return feature_dims, self.cont_cols
    
    def get_data_with_negatives(self, train_data, num_negatives=4):
        """
        train_data에 대해 네거티브 샘플링 후 최종 train_df 반환
        num_negatives: 정답(1) 하나당 오답(0)을 몇 개 만들 것인가
        cat_cols[0]이 'pid'
        cat_cols[1]이 'id'
        """
        # 아이템 피쳐 준비 (id 기준 중복 제거, artists 포함 모든 정보)
        # cat_cols[0]인 'pid'를 제외한 모든 아이템 속성 추출
        item_meta_cols = [c for c in self.cat_cols if c != self.cat_cols[0]] + self.cont_cols
        item_features = self.df[item_meta_cols].drop_duplicates(self.cat_cols[1])
        # 모든 id unique 값
        all_item_ids = self.df[self.cat_cols[1]].unique()
        
        rng = np.random.default_rng(self.random_state)
    
        neg_pids = []
        neg_items = []

        # 각 플레이리스트(pid)별로 그 안에 없는 곡을 샘플링
        for pid, group in tqdm(train_data.groupby(self.cat_cols[0]), desc="Negative Sampling"):
            pos_items = set(group[self.cat_cols[1]].values) # pos item 집합
            n_pos = len(group) # pos 개수
            n_neg_needed = n_pos * num_negatives # neg 필요 개수

            count = 0
            while count < n_neg_needed:
                # 한번에 (neg 필요 개수 - neg 현재 개수) 만큼 샘플링
                samples = rng.choice(all_item_ids, size=n_neg_needed - count)

                # 샘플링한 값이 pos item 집합에 없다면 neg item에 추가
                for s in samples:
                    if s not in pos_items:
                        neg_pids.append(pid)
                        neg_items.append(s)
                        count += 1
        
        # neg는 라벨 0
        neg_df = pd.DataFrame({
            self.cat_cols[0]: neg_pids,
            self.cat_cols[1]: neg_items,
            'label': 0
        })

        neg_df = neg_df.merge(item_features, on=self.cat_cols[1], how='left')

        # pos는 라벨 1
        train_df_copy = train_data.copy()
        train_df_copy['label'] = 1
        
        full_train_df = pd.concat([train_df_copy, neg_df], axis=0)
        
        # 순서 섞기 frac은 비율 (=1 이니까 전체를 뜻함)
        full_train_df = full_train_df.sample(frac=1, random_state=self.random_state).reset_index(drop=True)
        
        return full_train_df
    
    def transform_to_loader(self, df, batch_size, shuffle=True):
        """
        DataFrame -> PyTorch DataLoader 변환
        """
        # 범주형 및 수치형 데이터 변환
        cat_x = torch.LongTensor(df[self.cat_cols].values.copy())
        cont_x = torch.FloatTensor(df[self.cont_cols].values.copy())
        
        # 라벨 변환 (추론시 컬럼에 라벨이 없으므로 zeors)
        if 'label' in df.columns:
            label = torch.FloatTensor(df['label'].values.copy())
        else:
            label = torch.zeros(len(df), dtype=torch.float32)

        # Dataset 및 DataLoader 생성
        dataset = TensorDataset(cat_x, cont_x, label)
        return PyTorchDataLoader(dataset, batch_size=batch_size, shuffle=shuffle)