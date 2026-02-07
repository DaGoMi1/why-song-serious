import torch
import numpy as np
import pandas as pd
from tqdm import tqdm
import ast

class Evaluator:
    def __init__(self, retriever, model, loader, device):
        self.retriever = retriever
        self.model = model
        self.loader = loader
        self.device = device

    def evaluate(self, test_input, test_label, top_k=10):
        self.model.eval()
        all_user_recalls = []
        retrieval_recalls = []
        
        print(f"후보군 추출 및 리랭킹 시작 (Recall@{top_k})...")
        
        pbar = tqdm(test_input.groupby('pid'))

        for pid, group in pbar:
            seed_songs = group['id'].tolist()

            # 정답 곡 리스트
            actual_target = test_label[test_label['pid'] == pid]['id'].tolist()
            
            # 리트리벌 후보 추출
            candidates = self.retriever.retrieve(song_ids=seed_songs).copy()
            
            # 리트리벌 단계의 Recall (실제 정답 중 몇 개나 후보군에 포함되었나)
            retrieval_ids = candidates['id'].tolist()
            retrieval_hits = len(set(retrieval_ids) & set(actual_target))
            retrieval_recall = retrieval_hits / len(actual_target)
            retrieval_recalls.append(retrieval_recall)
            
            # 인기도 범주화
            # 리트리벌이 가져온 candidates에 'popularity'가 있으므로 똑같은 기준으로 binning
            if 'popularity' in candidates.columns:
                candidates['pop_grade'] = pd.cut(candidates['popularity'], 
                                                 bins=[0, 40, 60, 73, 80, 101], 
                                                 labels=[0, 1, 2, 3, 4], 
                                                 right=False).astype(int)

            # 리랭킹을 위한 데이터 변환 (pid 정보 주입)
            candidates['pid'] = pid
            
            # DeepFM 입력용 텐서 생성
            candidate_loader = self.loader.transform_to_loader(
                candidates, batch_size=len(candidates), shuffle=False
            )
            
            # 리랭킹 스코어 예측
            scores = []
            with torch.no_grad():
                for batch in candidate_loader:
                    x_cat, x_cont, _ = [b.to(self.device) for b in batch]
                    pred = self.model(x_cat, x_cont)
                    scores.extend(pred.cpu().numpy())
            
            candidates['score'] = scores
            
            # 상위 K개 추출 및 Recall 계산
            top_recs = candidates.sort_values(by='score', ascending=False).head(top_k)['id'].tolist()
            
            # 맞힌 개수 계산
            hits = len(set(top_recs) & set(actual_target))
            # Recall = (맞힌 개수) / (전체 정답 개수)
            recall = hits / len(actual_target)
            
            all_user_recalls.append(recall)

        # Recall@K 출력
        avg_retrieval_recall = np.mean(retrieval_recalls)
        avg_recall = np.mean(all_user_recalls)
        
        print(f"\nRetrieval Stage Recall@{self.retriever.retriever_k}: {avg_retrieval_recall:.4f}")
        print(f"Evaluation Results Recall@{top_k}: {avg_recall:.4f}")
        
        return avg_recall
    
class LightGCNEvaluator:
    def __init__(self, model, loader, device):
        self.model = model
        self.loader = loader
        self.device = device

        self.num_users = loader.num_users
        self.num_items = loader.num_items
        self.adj = loader.adj
        self.train_pos = loader.user_pos_train

    @torch.no_grad()
    def evaluate(self, test_input, test_label, k=10):
        self.model.eval()

        # Forward
        emb = self.model(self.adj)

        user_emb = emb[:self.num_users]          # (U, D)
        item_emb = emb[self.num_users:]          # (I, D)

        hits = 0
        total = 0

        print(f"[LightGCN] Recall@{k} 평가 시작...")

        # test_label: columns = ['uid', 'iid']
        for u, i in tqdm(
            zip(test_label['uid'], test_label['iid']),
            total=len(test_label)
        ):
            u = int(u)
            gt_i = int(i)

            # Score 계산
            scores = torch.matmul(user_emb[u], item_emb.T)

            # train에서 본 아이템 제거
            seen_items = list(self.train_pos[u])
            if len(seen_items) > 0:
                scores[seen_items] = -1e9

            # Top-K
            topk_items = torch.topk(scores, k).indices

            if gt_i in topk_items:
                hits += 1
            total += 1

        recall = hits / total

        print(f"[LightGCN] Evaluation Results Recall@{k}: {recall:.4f}")
        return recall