import torch

class SongRanker:
    def __init__(self, model, label_encoders, config, device='cpu'):
        self.model = model
        self.label_encoders = label_encoders
        self.config = config
        self.device = device
        self.model.to(self.device)
        self.model.eval()

        self.k = self.config['recommendation']['rerank_top_k']

        self.le_dicts = {}
        for col, le in self.label_encoders.items():
            self.le_dicts[col] = {str(cls): idx for idx, cls in enumerate(le.classes_)}

    def rank(self, candidates_df, pid=824067):
        input_df = candidates_df.copy()
        input_df['pid'] = pid
        
        cat_cols = list(self.label_encoders.keys())
        cont_cols = self.config['model']['continuous_features']

        # Label Encoding
        for col in cat_cols:
            if col in input_df.columns:
                mapping = self.le_dicts[col]
                input_df[col] = input_df[col].astype(str).map(mapping).fillna(0).astype(int)

        # 텐서 변환
        X_cat = torch.LongTensor(input_df[cat_cols].values).to(self.device)
        X_cont = torch.FloatTensor(input_df[cont_cols].values).to(self.device)

        # 예측
        with torch.no_grad():
            scores = self.model(categorical_x=X_cat, continuous_x=X_cont).cpu().numpy().flatten()
        
        result_df = candidates_df.copy()
        result_df['model_score'] = scores
        
        final_output = result_df.sort_values(by='model_score', ascending=False).head(self.k)
        
        return final_output[['id', 'name', 'model_score']]