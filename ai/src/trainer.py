import os
import torch
from tqdm import tqdm
from src.losses import manual_bce_with_logits_loss

class Trainer:
    def __init__(self, model, optimizer, loss_pos_weight, device, checkpoint_dir="./checkpoints", file_name="기본"):
        self.model = model
        self.optimizer = optimizer
        self.criterion = manual_bce_with_logits_loss
        self.loss_pos_weight = loss_pos_weight
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
            loss = self.criterion(output.squeeze(), label, pos_weight=self.loss_pos_weight)
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
                loss = self.criterion(output.squeeze(), label, pos_weight=self.loss_pos_weight)
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