import torch

class EASE:
    def __init__(self, lambda_):
        self.lambda_ = lambda_
        self.B = None
        self.item_size = None

    def fit(self, X):
        #  (X.T@X + λI)−1
        self.item_size = X.shape[1]
        I = torch.eye(self.item_size, device=X.device)
        P = torch.linalg.inv(X.T @ X + self.lambda_ * I)

        # B = I - P * diagMat (1 / diag(P))
        self.B = P / - torch.diagonal(P)
        
        diag_indices = torch.arange(self.B.shape[0], device=X.device)
        self.B[diag_indices, diag_indices] = 0
    
    def forward(self, X):
        return X @ self.B
