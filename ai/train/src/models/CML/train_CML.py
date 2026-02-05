import torch.optim as optim
from tqdm import tqdm
import torch
import pandas as pd
from torch.utils.data import DataLoader
from CML import CML, CMLSet

def train(csv_dir="/data/ephemeral/home/data/add_feature_v3.csv",
          mapping_dir="/data/ephemeral/home/data/item_label_mapping.csv") -> pd.DataFrame:
    """
    CML 모델을 학습시킨 후 아이템 임베딩을 df 형식으로 반환합니다.

    :param : 학습할 csv 파일의 경로
    """

    # 1. 하이퍼 파라미터 세팅
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"device is {device}")
    lr = 0.01
    epochs = 10
    batch_size = 8192
    neg_size = 5

    df = pd.read_csv(csv_dir)
    n_playlists = df['pid'].max() + 1
    del df
    
    df = pd.read_csv(mapping_dir)
    n_items = df['index'].max() + 1

    del df

    # 2. 데이터셋 로드 및 데이터로더 생성
    train_set = CMLSet(n_items=n_items, neg_size=neg_size)
    train_loader = DataLoader(train_set, batch_size=batch_size, shuffle=True, num_workers=6, persistent_workers=True, pin_memory=True)

    # 3. 모델 초기화
    model = CML(n_playlists=n_playlists, n_items=n_items, embed_dim=64).to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr, weight_decay=0.001)

    # 4. 모델 학습
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        progress_bar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs}")
        
        for pids, items in progress_bar:
            pids = pids.to(device)
            items = items.to(device)
            optimizer.zero_grad()
            
            pos_ids = items[:, 0].unsqueeze(1)
            neg_ids = items[:, 1:]
            
            # model loss 계산
            loss = model.calculate_loss(pids, pos_ids, neg_ids)
            
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            progress_bar.set_postfix(loss=loss.item())
        
        avg_loss = total_loss / len(train_loader)
        print(f"Epoch {epoch+1} Average Loss: {avg_loss:.4f}")

    item_vectors = model.item.weight.detach().to('cpu').numpy()

    mapping = pd.read_csv("/data/ephemeral/home/data/item_label_mapping.csv")
    df = pd.DataFrame({})
    df['id'] = mapping['song_id']
    for i in range(item_vectors.shape[1]):
        df[f"emb{i}"] = item_vectors[:,i]

    return df

if __name__=="__main__":
    df = train()
    df.to_csv("/data/ephemeral/home/clustering/embs/CML_embeddings.csv", index=False)
