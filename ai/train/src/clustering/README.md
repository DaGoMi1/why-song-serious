# Cluster-based Music Recommendation Explanation

이 프로젝트는 **음악 추천 시스템에서 생성된 군집(cluster)에 대해 사용자에게 보여줄 “추천 이유 설명 문구”를 자동 생성**하기 위한 모듈이다.

임베딩 기반으로 군집의 대표 곡을 선정하고, 오디오 특성 통계를 요약한 뒤 Hugging Face의 Gemma LLM을 사용해 자연스러운 한국어 설명 문장을 생성한다.

## 목적

"왜 이 음악들이 추천되었는가?"를 **사용자가 이해할 수 있는 문장으로 설명**

추천 결과의 **해석 가능성(Explainability)** 강화

## 프로젝트 구조
```
ai/feature/explanation/
│
├── data/                         # 입력 데이터 (※ GitHub 미포함, 대용량)
│   ├── item_label_mapping.csv
│   ├── item_embedding.npy
│   ├── for_cluster.json
│   └── add_feature_v3.csv
│
├── src/                          # 실행 코드
│   ├── generate_cluster_description.py  # 설명 생성
│   └── prompt.py                 # LLM 프롬프트 템플릿
│
├── output/                       # 생성 결과
│   └── cluster_description.json
│
├── .env                          # HuggingFace Token
├── .gitignore
└── README.md
```
## 사용모델

- Model : google/gemma-3-4b-it
- Model Link : https://huggingface.co/google/gemma-3-4b-it
- Platform : Hugging Face Transformers
- **유의사항** : Gemma 모델은 Hugging Face 인증을 필요로 함.
- 인증 불필요한 대체 모델 : Qwen/Qwen2.5-3B-Instruct

## Hugging Face Token 설정

.env 파일을 생성하고 아래 내용을 추가한다
```
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx
```

## 실행 방법
```
# 의존성 설치
pip install -r requirements.txt

# 실행
python src/generate_cluster_description.py
```
실행 완료 시 결과: 
```
output/cluster_description.json
```
파일이 생성된다.

## 출력 예시
```
{
  "12": "리듬감 있는 사운드와 낮은 감성 톤의 곡들을 선호하는 취향을 반영한 추천입니다.",
  "13": "에너지가 높고 대중적인 분위기의 음악을 즐기는 성향에 맞춘 곡들입니다."
}
```
- key : 군집 ID
- value : 사용자에게 노출될 추천 이유 문장

  
