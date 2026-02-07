import pandas as pd
import numpy as np
import torch
from collections import defaultdict
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import coo_matrix

class LightGCNDataLoader:
    def __init__(
        self,
        file_path: str,
        test_size: float = 0.1,
        hidden_count: int = 1,     # LightGCN은 보통 last-item holdout
        random_state: int = 42,
        device: torch.device = "cuda"
    ):
        self.file_path = file_path
        self.test_size = test_size
        self.hidden_count = hidden_count
        self.random_state = random_state
        self.device = device

        self.df = pd.read_csv(file_path)

        # encoders
        self.user_encoder = LabelEncoder()
        self.item_encoder = LabelEncoder()

        self.num_users = None
        self.num_items = None
        self.adj = None

        self.user_pos_train = defaultdict(set)

    def prepare(self):
        df = self.df.copy(deep=True)

        df['uid'] = self.user_encoder.fit_transform(df['pid'])
        df['iid'] = self.item_encoder.fit_transform(df['id'])

        self.num_users = df['uid'].nunique()
        self.num_items = df['iid'].nunique()

        df = df.sort_values(['uid'])

        train_rows, test_rows = [], []

        for u, g in df.groupby('uid'):
            train_rows.append(g.iloc[:-self.hidden_count])
            test_rows.append(g.iloc[-self.hidden_count:])

        train_df = pd.concat(train_rows)
        test_df = pd.concat(test_rows)

        for u, i in zip(train_df['uid'], train_df['iid']):
            self.user_pos_train[int(u)].add(int(i))

        rows = train_df['uid'].values
        cols = train_df['iid'].values + self.num_users
        data = np.ones(len(rows))

        adj = coo_matrix(
            (data, (rows, cols)),
            shape=(self.num_users + self.num_items,
                self.num_users + self.num_items)
        )

        adj = adj + adj.T
        adj = self._normalize_adj(adj)
        self.adj = self._to_sparse_tensor(adj).to(self.device)

        train_data = {
            "adj": self.adj,
            "user_pos": self.user_pos_train,
            "users": list(self.user_pos_train.keys()),
            "num_items": self.num_items
        }

        test_input = test_df[['uid']]
        test_label = test_df[['uid', 'iid']]

        return train_data, test_input, test_label
    
    def _normalize_adj(self, adj):
        rowsum = np.array(adj.sum(1)).flatten()
        d_inv_sqrt = np.power(rowsum, -0.5)
        d_inv_sqrt[np.isinf(d_inv_sqrt)] = 0.0

        d_mat = coo_matrix(
            (d_inv_sqrt, (np.arange(len(rowsum)), np.arange(len(rowsum))))
        )

        return d_mat @ adj @ d_mat

    def _to_sparse_tensor(self, mat):
        mat = mat.tocoo()
        indices = torch.LongTensor([mat.row, mat.col])
        values = torch.FloatTensor(mat.data)
        return torch.sparse.FloatTensor(indices, values, mat.shape)