import torch
import pandas as pd

class SongRanker:
    def __init__(self, model, label_encoders, item_meta, config, device='cpu'):
        self.model = model
        self.label_encoders = label_encoders  # LabelEncoder 객체들이 담긴 딕셔너리
        self.item_meta = item_meta.set_index('id', drop=False)
        self.config = config
        self.device = device
        self.model.to(self.device)
        self.model.eval()
        
        # 설정 파일에서 가져오기
        self.k = self.config['recommendation']['rerank_top_k']
        self.cat_cols = self.config['model']['cat_cols']

        self.id_map = {cls: idx for idx, cls in enumerate(self.label_encoders['id'].classes_)}
        self.inv_id_map = {idx: cls for cls, idx in self.id_map.items()}

    def rank(self, candidate_org_ids, pid):
        candidate_enc_ids = [self.id_map[oid] for oid in candidate_org_ids if oid in self.id_map]

        # deepfm_df에서 해당 enc_id 행들 추출
        input_df = self.item_meta[self.item_meta['id'].isin(candidate_enc_ids)].copy()

        # 유저 ID(pid) 인코딩 처리
        le_pid = self.label_encoders['pid']
        pid_str = str(pid)
        encoded_pid = le_pid.transform([pid_str])[0] if pid_str in le_pid.classes_ else 0
        input_df['pid'] = encoded_pid
        
        # 모델 입력용 텐서 생성
        X_cat = torch.LongTensor(input_df[self.cat_cols].values).to(self.device)

        # DeepFM 추론
        with torch.no_grad():
            scores = self.model(X_cat)
            scores = scores.cpu().numpy().flatten()

        # 최종 결과 정리
        input_df['model_score'] = scores

        top_k_df = input_df.sort_values(by='model_score', ascending=False).head(self.k).copy()
        top_k_df['org_id'] = top_k_df['id'].map(self.inv_id_map)
        
        return top_k_df[['org_id', 'name', 'model_score']]