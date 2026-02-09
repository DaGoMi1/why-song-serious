import os
import torch
from tqdm import tqdm
from src.losses import manual_bce_with_logits_loss
from src.losses import focal_binary_cross_entropy_with_logits

class DeepFMTrainer:
    def __init__(self, model, optimizer, loss_pos_weight, loss_alpha, loss_gamma, device, checkpoint_dir="./checkpoints", file_name="기본"):
        self.model = model
        self.optimizer = optimizer
        self.criterion = focal_binary_cross_entropy_with_logits
        self.loss_pos_weight = loss_pos_weight
        self.loss_alpha=loss_alpha
        self.loss_gamma=loss_gamma
        self.device = device
        self.checkpoint_dir = checkpoint_dir
        self.file_name = file_name

    def train_one_epoch(self, train_loader):
        self.model.train()
        total_loss = 0

        pbar = tqdm(enumerate(train_loader), total=len(train_loader), desc="Training")

        for i, (cat_x, cont_x, label) in pbar:
            cat_x, cont_x, label = cat_x.to(self.device), cont_x.to(self.device), label.to(self.device)

            self.optimizer.zero_grad()
            output = self.model(cat_x, cont_x)
            loss = self.criterion(output.squeeze(), label, alpha=0.8, gamma=2.0)
            loss.backward()
            self.optimizer.step()

            total_loss += loss.item()

            if i % 1000 == 0:
             pbar.set_postfix(loss=f"{loss.item():.4f}")
        
        return total_loss / len(train_loader)

    def evaluate(self, valid_loader):
        self.model.eval()
        total_loss = 0
        with torch.no_grad():
            for cat_x, cont_x, label in valid_loader:
                cat_x, cont_x, label = cat_x.to(self.device), cont_x.to(self.device), label.to(self.device)

                output = self.model(cat_x, cont_x)
                loss = self.criterion(output.squeeze(), label, alpha=0.8, gamma=2.0)
                total_loss += loss.item()

        return total_loss / len(valid_loader)
    
    def train(self, train_loader, valid_loader, epochs):
        best_loss = float('inf')
        final_save_path = os.path.join(self.checkpoint_dir, f"{self.file_name}_best_model.pt")

        for epoch in range(epochs):
            train_loss = self.train_one_epoch(train_loader)
            valid_loss = self.evaluate(valid_loader)
            
            print(f"Epoch {epoch+1:02d}/{epochs} | Train Loss: {train_loss:.4f} | Valid Loss: {valid_loss:.4f}")

            if valid_loss < best_loss:
                best_loss = valid_loss
                torch.save(self.model.state_dict(), final_save_path)
                print(f"Best model saved at {final_save_path}")
        
        print("=" * 30)
        print(f"학습 완료! 최적 모델 경로: {final_save_path}")

class LightGCNTrainer:
    # LightGCN Trainer (BPR Loss)
    
    def __init__(
        self,
        model,
        optimizer,
        train_data,
        num_negatives,
        device,
        checkpoint_dir="./checkpoints",
        file_name="lightgcn"
    ):
        self.model = model
        self.optimizer = optimizer
        self.train_data = train_data
        self.num_negatives = num_negatives
        self.device = device

        self.checkpoint_dir = checkpoint_dir
        self.file_name = file_name

        self.user_pos = train_data["user_pos"]
        self.users = train_data["users"]
        self.num_items = train_data["num_items"]

    def sample_neg(self, u):
        while True:
            neg = torch.randint(0, self.num_items, (1,)).item()
            if neg not in self.user_pos[u]:
                return neg

    def bpr_loss(self, u_emb, pos_emb, neg_emb):
        pos = (u_emb * pos_emb).sum(dim=1)
        neg = (u_emb * neg_emb).sum(dim=1)
        return (-torch.log(torch.sigmoid(pos - neg) + 1e-8)).mean()

    def train(self, epochs):
        best_loss = float("inf")
        save_path = os.path.join(
            self.checkpoint_dir,
            f"{self.file_name}_best_model.pt"
        )

        for epoch in range(epochs):
            self.model.train()
            total_loss = 0

            pbar = tqdm(self.users, desc=f"[LightGCN] Epoch {epoch+1}")
            for u in pbar:
                u = int(u)
                for pos in self.user_pos[u]:
                    for _ in range(self.num_negatives):
                        neg = self.sample_neg(u)

                        self.optimizer.zero_grad()
                        emb = self.model(self.model.adj)

                        u_emb = emb[u]
                        p_emb = emb[self.model.num_users + pos]
                        n_emb = emb[self.model.num_users + neg]

                        loss = self.bpr_loss(
                            u_emb.unsqueeze(0),
                            p_emb.unsqueeze(0),
                            n_emb.unsqueeze(0)
                        )

                        loss.backward()
                        self.optimizer.step()

                        total_loss += loss.item()
                        pbar.set_postfix(loss=f"{loss.item():.4f}")

            avg_loss = total_loss / max(1, len(self.users))
            print(f"[LightGCN] Epoch {epoch+1} Loss: {avg_loss:.4f}")

            if avg_loss < best_loss:
                best_loss = avg_loss
                torch.save(self.model.state_dict(), save_path)
                print(f"Best model saved at {save_path}")

        print("=" * 30)
        print(f"[LightGCN] 학습 완료! 최적 모델 경로: {save_path}")