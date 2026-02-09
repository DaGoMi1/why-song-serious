import torch
import torch.nn as nn

class DeepFM(nn.Module):
    def __init__(self, feature_dims, embedding_dim, hidden_layers=[128, 64], dropout=0.2):
        super().__init__()
        # 임베딩 차원
        self.embedding_dim = embedding_dim

        # 임베딩: 모든 필드를 동일 차원으로 맵핑
        self.embeddings = nn.ModuleList([nn.Embedding(dim, embedding_dim) for feat, dim in feature_dims.items()])

        # FM 1차항 (선형)
        self.linear = nn.Linear(len(feature_dims), 1)

        # DNN (고차원)
        input_dim = len(feature_dims) * embedding_dim
        layers = []
        for h in hidden_layers:
            layers.append(nn.Linear(input_dim, h))
            layers.append(nn.BatchNorm1d(h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            input_dim = h
        layers.append(nn.Linear(input_dim, 1))
        self.dnn = nn.Sequential(*layers)

    def forward(self, x):
        # 임베딩
        embedded_list = [emb(x[:, i]) for i, emb in enumerate(self.embeddings)]
        embeddings = torch.stack(embedded_list, dim=1) # [B, N, D]

        # Linear Part- 1차항
        out_linear = self.linear(x.float())

        # FM Part - 2차항 상호작용
        sum_of_embed = torch.sum(embeddings, dim=1) # [B, D]
        square_of_sum = sum_of_embed.pow(2)
        sum_of_square = torch.sum(embeddings.pow(2), dim=1)
        
        # 차원(D) 방향으로 합산하여 [B, 1]로 만듦
        out_interaction = 0.5 * torch.sum(square_of_sum - sum_of_square, dim=1, keepdim=True)

        # Deep Part
        flat_embed = embeddings.view(embeddings.size(0), -1) # [B, N*D]
        out_deep = self.dnn(flat_embed)

        # 최종 결합
        # 로짓값 그대로 활용하는 로스 함수 사용중이라서 sigmoid로 반환하지 않음
        output = out_linear + out_interaction + out_deep

        return output.squeeze()