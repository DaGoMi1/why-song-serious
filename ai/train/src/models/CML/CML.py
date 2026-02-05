import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder

class CML(nn.Module):
    def __init__(self, n_playlists, n_items, embed_dim=64, margin=0.5, lambda_cov=0.001):
        super().__init__()
        self.margin = margin
        self.lambda_cov = lambda_cov

        self.playlist = nn.Embedding(n_playlists, embed_dim)
        self.item = nn.Embedding(n_items, embed_dim)
        
        nn.init.normal_(self.playlist.weight, std=0.01)
        nn.init.normal_(self.item.weight, std=0.01)

    def forward(self, p, i):
        playlist = F.normalize(self.playlist(p).unsqueeze(1), p=2, dim=-1)
        item = F.normalize(self.item(i), p=2, dim=-1)

        dist = torch.sum((playlist - item)**2, dim=-1)

        return dist

    def calculate_loss(self, playlist, pos, neg):
        pos_dist = self.forward(playlist, pos)
        neg_dist = self.forward(playlist, neg)

        triplet_loss = F.relu(self.margin + pos_dist - neg_dist).mean()
        
        all_item_ids = torch.cat([pos.contiguous().view(-1), neg.contiguous().view(-1)])
        batch_item_embs = self.item(all_item_ids) 
        
        reg_loss = self._covariance_regularization(batch_item_embs)
        return triplet_loss + (self.lambda_cov * reg_loss)
    
    def _covariance_regularization(self, embeddings):
        n, d = embeddings.size()

        mu = embeddings.mean(dim=0)
        x = embeddings - mu

        cov = (x.T @ x) / (n - 1)
        diag_mask = torch.eye(d).to(embeddings.device)
        off_diag_cov = cov * (1 - diag_mask)
        loss_cov = torch.sum(off_diag_cov ** 2)
        return loss_cov

        
class CMLSet(Dataset):
    def __init__(self, n_items, neg_size):
        super().__init__()
        self.n_items = n_items
        self.neg_size = neg_size

        df = pd.read_csv("/data/ephemeral/home/data/add_feature_v3.csv")
        mapping = pd.read_csv("/data/ephemeral/home/data/item_label_mapping.csv")
        le = LabelEncoder()
        le = le.fit(mapping['song_id'])
        df['id'] = le.transform(df['id'])
        
        self.pid = torch.from_numpy(df['pid'].values).to(torch.long)
        self.tid = torch.from_numpy(df['id'].values).to(torch.long)
        
    def __len__(self):
        return len(self.pid)
    
    def __getitem__(self, idx):
        pos = self.tid[idx].reshape(1)
        neg = torch.randint(0, self.n_items, (self.neg_size,))
        items = torch.cat([pos, neg])
        return self.pid[idx], items
