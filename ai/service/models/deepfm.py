import torch
import torch.nn as nn

class DeepFM(nn.Module):
    def __init__(self, feature_dims, embedding_dim, continuous_cols, hidden_layers=[256, 128, 64], dropout=0.4):
        super().__init__()

        self.continuous_cols = continuous_cols
        self.embedding_dim = embedding_dim

        self.embeddings = nn.ModuleList([
            nn.Embedding(dim, embedding_dim) for feat, dim in feature_dims.items()
        ])

        self.linear = nn.Linear(len(feature_dims) + len(continuous_cols), 1)

        input_dim = len(feature_dims) * embedding_dim + len(continuous_cols)

        layers = []
        for h in hidden_layers:
            layers.append(nn.Linear(input_dim, h))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(dropout))
            input_dim = h
        
        # 마지막 레이어 (Deep 파트의 결과를 1개의 점수로 요약)
        layers.append(nn.Linear(input_dim, 1))
        
        self.dnn = nn.Sequential(*layers)

    def forward(self, categorical_x, continuous_x):
        embedded_list = [emb(categorical_x[:, i]) for i, emb in enumerate(self.embeddings)]
        embeddings = torch.stack(embedded_list, dim=1)

        linear_input = torch.cat([categorical_x.float(), continuous_x], dim=1)
        out_linear = self.linear(linear_input)

        sum_of_embed = torch.sum(embeddings, dim=1)
        square_of_sum = sum_of_embed.pow(2)
        sum_of_square = torch.sum(embeddings.pow(2), dim=1)
        out_interaction = 0.5 * torch.sum(square_of_sum - sum_of_square, dim=1, keepdim=True)

        flat_embed = embeddings.view(embeddings.size(0), -1)
        deep_input = torch.cat([flat_embed, continuous_x], dim=1)
        out_deep = self.dnn(deep_input)

        output = out_linear + out_interaction + out_deep

        return output.squeeze()