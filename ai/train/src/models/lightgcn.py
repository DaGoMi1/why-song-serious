import torch
import torch.nn as nn


class LightGCN(nn.Module):

    def __init__(
        self,
        num_users: int,
        num_items: int,
        embedding_dim: int = 64,
        n_layers: int = 2
    ):
        super().__init__()

        self.num_users = num_users
        self.num_items = num_items
        self.n_layers = n_layers
        self.embedding_dim = embedding_dim

        self.embedding = nn.Embedding(
            num_embeddings=num_users + num_items,
            embedding_dim=embedding_dim
        )

        nn.init.xavier_uniform_(self.embedding.weight)

    def forward(self, adj: torch.sparse.FloatTensor):
        all_emb = self.embedding.weight
        emb_list = [all_emb]

        for _ in range(self.n_layers):
            all_emb = torch.sparse.mm(adj, all_emb)
            emb_list.append(all_emb)

        emb_stack = torch.stack(emb_list, dim=1)
        final_emb = emb_stack.mean(dim=1)

        return final_emb

    def get_user_item_embedding(self, adj):
        emb = self.forward(adj)
        user_emb = emb[:self.num_users]
        item_emb = emb[self.num_users:]
        return user_emb, item_emb