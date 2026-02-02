"""
DeepFM 모델 추론 모듈

현재는 Mock 구현. 모델 받으면 실제 추론으로 교체.
"""

import numpy as np
from pathlib import Path


class DeepFMInference:
    """DeepFM 모델 추론 클래스"""
    
    def __init__(self, model_path: str | None = None):
        """
        Args:
            model_path: ONNX 또는 PyTorch 모델 파일 경로
        """
        self.model_path = model_path
        self.model = None
        
        if model_path and Path(model_path).exists():
            self._load_model()
        else:
            print("DeepFM: Mock 모드로 실행 (모델 파일 없음)")
    
    def _load_model(self):
        """모델 로딩 - AI 팀 모델 받으면 구현"""
        # TODO: 실제 모델 로딩 구현
        # import onnxruntime as ort
        # self.model = ort.InferenceSession(self.model_path)
        pass
    
    def get_embedding(self, preferences: list[float]) -> list[float]:
        """
        preference 값으로부터 64차원 임베딩 생성
        
        Args:
            preferences: 6개의 정규화된 feature 값 (0.0 ~ 1.0)
            
        Returns:
            64차원 임베딩 벡터
        """
        if self.model is not None:
            # TODO: 실제 모델 추론
            # input_array = np.array([preferences], dtype=np.float32)
            # outputs = self.model.run(None, {"input": input_array})
            # return outputs[0][0].tolist()
            pass
        
        # Mock: preference 기반 deterministic 임베딩 생성
        return self._mock_embedding(preferences)
    
    def _mock_embedding(self, preferences: list[float]) -> list[float]:
        """
        Mock 임베딩 생성
        
        동일한 preference 입력에 대해 동일한 임베딩 반환 (재현성)
        """
        # preference를 seed로 사용해 재현 가능한 벡터 생성
        seed = int(sum(p * (10 ** i) for i, p in enumerate(preferences)) * 1000)
        rng = np.random.default_rng(seed)
        
        vec = rng.standard_normal(64)
        vec = vec / np.linalg.norm(vec)  # L2 정규화
        
        return vec.tolist()


# 싱글톤 인스턴스
_inference_instance: DeepFMInference | None = None


def get_deepfm_inference() -> DeepFMInference:
    """DeepFM 추론 인스턴스 반환 (싱글톤)"""
    global _inference_instance
    
    if _inference_instance is None:
        # 모델 경로 설정 (있으면 로딩, 없으면 Mock)
        model_path = "ml_models/deepfm/model.onnx"
        _inference_instance = DeepFMInference(model_path)
    
    return _inference_instance
