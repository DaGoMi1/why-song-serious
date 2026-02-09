import yaml
import torch
import os
import torch.optim as optim
import numpy as np
import joblib
from src.dataloaders import DeepFMDataLoader
from src.retriever import Retriever
from src.models.deepfm import DeepFM
from src.trainer import Trainer
from src.evaluator import Evaluator
from src.utils import set_seed

from src.dataloaders.lightgcn_loader import LightGCNDataLoader
from src.models.lightgcn import LightGCN
from src.trainer import LightGCNTrainer
from src.evaluator import LightGCNEvaluator

from src.dataloaders.ease_loader import EASEDataLoader
from src.models.ease import EASE
from src.evaluator import EASEEvaluator

def main():
    # Config 로드
    with open('./configs/base_config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 전역 설정 및 모델 선택
    global_cfg = config['global']
    use_model = config['use']               # 사용 모델
    m_cfg = config['models'][use_model]     # 현재 사용할 모델의 상세 설정

    # 시드 고정 및 device 설정
    set_seed(global_cfg['random_state'])
    device = torch.device(global_cfg['device'] if torch.cuda.is_available() else "cpu")

    # 데이터 로딩
    print(f"[{use_model}] 데이터 로드 및 전처리 시작...")

    if use_model == 'deepfm':
        d_cfg = config['data']
        m_params = m_cfg['params']
        m_feat = m_cfg['features']
        m_train = m_cfg['train']
        
        # 데이터 로더 클래스 생성
        loader = DeepFMDataLoader(
            file_path=config['data']['path'],
            cat_cols=m_feat['categorical'],
            cont_cols=m_feat['continuous'],
            random_state=global_cfg['random_state']
        )

        # 데이터 전처리
        feature_dims, continuous_cols = loader.preprocess()

        # 데이터 분할
        train_df, valid_df, test_input, test_label = loader.split_data(
            test_size=d_cfg['test_size'],
            hidden_count=d_cfg['hidden_count']
        )

        # 네거티브 샘플링
        train_df_final = loader.get_data_with_negatives(train_df, num_negatives=m_train['num_negatives'])
        valid_df_final = loader.get_data_with_negatives(valid_df, num_negatives=m_train['num_negatives'])
        
        # 데이터 로더 형식으로 변경
        train_loader = loader.transform_to_loader(train_df_final, batch_size=m_train['batch_size'])
        valid_loader = loader.transform_to_loader(valid_df_final, batch_size=m_train['batch_size'], shuffle=False)

        # 모델 불러오기
        model = DeepFM(
            feature_dims=feature_dims,
            embedding_dim=m_params['embedding_dim'],
            continuous_cols=continuous_cols,
            hidden_layers=m_params['hidden_layers'],
            dropout=m_params['dropout']
        ).to(device)

        # 옵티마이저
        optimizer = getattr(optim, m_train.get('optimizer', 'Adam'))(
            model.parameters(), 
            lr=float(m_train['learning_rate']),
            weight_decay=float(m_train['weight_decay'])
        )

        # 트레이너
        trainer = Trainer(
            model=model, 
            optimizer=optimizer,
            loss_pos_weight=m_train['loss_pos_weight'],
            device=device,
            checkpoint_dir=global_cfg['checkpoint_dir'],
            file_name=global_cfg['file_name']
        )

        # 학습
        print(f"{use_model} 학습 시작...")
        trainer.train(
            train_loader=train_loader,
            valid_loader=valid_loader, 
            epochs=m_train['epochs']
        )

        print("===== 최종 평가 시작 =====")
        best_model_path = os.path.join(global_cfg['checkpoint_dir'], f"{global_cfg['file_name']}_best_model.pt")

        if os.path.exists(best_model_path):
            print(f"최적 모델 로드 중: {best_model_path}")
            model.load_state_dict(torch.load(best_model_path, map_location=device))
        else:
            print("최적 모델 파일을 찾을 수 없어 현재 상태로 평가를 진행합니다.")

        inf_cfg = config['inference']

        # 리트리벌 및 평가 로직
        retriever = Retriever(
            audio_cols=m_feat['continuous'], # 모델별 피처 반영
            retriever_k=inf_cfg['retrieval']['top_k'],
            label_encoders=loader.label_encoders
        )

        retriever.prepare_data(
            file_path=config['data']['path']
        )

        # 평가기 실행
        evaluator = Evaluator(
            retriever=retriever, 
            model=model, 
            loader=loader, 
            device=device
        )
        
        # Recall@10 계산 (test_input 전체를 대상으로 루프 실행)
        final_recall = evaluator.evaluate(
            test_input=test_input, 
            test_label=test_label, 
            top_k=inf_cfg['reranking']['top_k']
        )

    elif use_model == 'lightgcn':
        d_cfg = config['data']
        m_params = m_cfg['params']
        m_train = m_cfg['train']
        m_eval = m_cfg.get('evaluation', {})

        print(f"[{use_model}] 데이터 로드 및 그래프 생성 시작...")

        # 1. 데이터 로더
        loader = LightGCNDataLoader(
            file_path=d_cfg['path'],
            test_size=d_cfg['test_size'],
            hidden_count=d_cfg['hidden_count'],
            random_state=global_cfg['random_state'],
            device=device
        )

        train_data, test_input, test_label = loader.prepare()

        # 2. 모델
        model = LightGCN(
            num_users=loader.num_users,
            num_items=loader.num_items,
            embedding_dim=m_params['embedding_dim'],
            n_layers=m_params['n_layers']
        ).to(device)

        # 3. 옵티마이저
        optimizer = getattr(optim, m_train.get('optimizer', 'Adam'))(
            model.parameters(),
            lr=float(m_train['learning_rate']),
            weight_decay=float(m_train.get('weight_decay', 0.0))
        )

        # 4. Trainer (BPR loss)
        trainer = LightGCNTrainer(
            model=model,
            optimizer=optimizer,
            train_data=train_data,
            num_negatives=m_train['num_negatives'],
            device=device,
            checkpoint_dir=global_cfg['checkpoint_dir'],
            file_name=global_cfg['file_name']
        )

        print(f"{use_model} 학습 시작...")
        trainer.train(epochs=m_train['epochs'])

        # 5. Best model load
        best_model_path = os.path.join(
            global_cfg['checkpoint_dir'],
            f"{global_cfg['file_name']}_best_model.pt"
        )

        if os.path.exists(best_model_path):
            print(f"최적 모델 로드 중: {best_model_path}")
            model.load_state_dict(torch.load(best_model_path, map_location=device))

        # 6. 평가
        evaluator = LightGCNEvaluator(
            model=model,
            loader=loader,
            device=device
        )

        final_recall = evaluator.evaluate(
            test_input=test_input,
            test_label=test_label,
            k=m_eval.get('k', config['inference']['reranking']['top_k'])
        )
    
    elif use_model == 'ease':
        import time
        d_cfg = config['data']
        l_list = m_cfg['lambda_list']
        
        # 데이터 로더 클래스 생성
        loader = EASEDataLoader(
            file_path=config['data']['path'],
            device=device,
            random_state=global_cfg['random_state']
        )

        # 데이터 전처리
        matrix = loader.preprocess()

        # 데이터 분할
        train, test_input, test_label = loader.split_data(
            matrix,
            test_size=d_cfg['test_size'],
            hidden_count=d_cfg['hidden_count']
        )

        # 하이퍼파라미터 튜닝
        best_lambda = 0.0
        best_recall = 0.0

        for i, l in enumerate(l_list):
            start_time = time.time()
            # 학습
            print(f"{use_model} 학습 시작... lambda={l}")
            model = EASE(l)

            model.fit(train)

            end_time = time.time()

            # 평가기 실행
            evaluator = EASEEvaluator(
                model=model,
            )
            
            # Recall@10 계산 (test_input 전체를 대상으로 루프 실행)
            final_recall = evaluator.evaluate(
                input=test_input,
                label=test_label,
                k=config['inference']['reranking']['top_k']
            )
            print(f"{i}번째 학습: {end_time - start_time}초 소요됐습니다.")
            
            if best_recall < final_recall:
                best_lambda = l
                best_recall = final_recall
                
        print(f"모델 재학습(lambda={best_recall})")
        model = EASE(best_lambda)
        matrix = torch.FloatTensor(matrix).to(device)
        model.fit(matrix)

        best_model_path = global_cfg['checkpoint_dir']+"ease_best_B.npy"
        
        # 모델 및 라벨인코더 저장
        np.save("checkpoints/best_B.npy",
                model.B.detach().cpu().numpy())
        joblib.dump(loader.label_encoders['id'],
                    "checkpoints/label_encoder_ease.joblib")


if __name__ == "__main__":
    main()