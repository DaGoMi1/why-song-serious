# 파일 구조

```
.
├── ai/
├── backend/
├── frontend/
├── .gitignore
└── README.md
```
<details>
   <summary><h2>AI</h2></summary>

```
ai/
├── inference/
│   ├── service_assets/
│   └── src/
│       ├── api/
│       ├── config/
│       ├── core/
│       ├── models/
│       └── main.py
├── train/
│   ├── checkpoints/
│   ├── configs/
│   ├── data/
│   ├── src/
│   │   ├── clustering/
│   │   ├── dataloaders/
│   │   ├── models/
│   │   ├── evaluator.py
│   │   ├── filtering.py
│   │   ├── losses.py
│   │   ├── retriever.py
│   │   ├── trainer.py
│   │   └── utils.py
│   └── main.py
└── requirements.txt

```
</details>
<details>
   <summary><h2>BE</h2></summary>

```
backend/
├── alembic/
├── app/
│   ├── auth/
│   ├── common/
│   ├── domain/
│   │   ├── cluster/
│   │   ├── interaction/
│   │   ├── playlist/
│   │   ├── preference/
│   │   ├── recommendation/
│   │   ├── track/
│   │   └── user/
│   ├── config.py
│   ├── database.py
│   └── main.py
├── README.md
├── alembic.ini
└── pyproject.toml
```
</details>
<details>
   <summary><h2>FE</h2></summary>

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   ├── data/
│   ├── pages/
│   │   ├── Discover.tsx
│   │   ├── Landing.tsx
│   │   ├── Playlist.tsx
│   │   └── Preferences.tsx
│   ├── stores/
│   ├── types/
│   ├── App.tsx
│   ├── index.css
│   ├── main.tsx
│   └── routes.ts
├── package.json
└── README.md
```
</details>

# 모델

## 모델 선정

Two-Stage (Faiss&DeepFM)

DeepFM: FM과 DNN의 장점을 결합하여 플레이리스트(pid)와 곡(id)의 단순한 관계도 포착 가능하며 템포, 에너지 등의 여러 오디오 피처와 곡(id)간의 복잡한 관계도 학습 가능, Cold-Start 상황에서는 오디오 피처를 통해 곡들의 특징을 기반으로 더 나은 추천이 가능

Faiss: 딥러닝 모델의 느린 연산 속도를 서비스 상황에서 잘 활용할 수 있도록 ANN알고리즘을 활용한 벡터 검색 방식인 Faiss를 활용하여 빠르게 후보군을 추출

## 모델 고도화

### 데이터 불균형 및 인기도 편향 해결

Feature Binning: 연속형 오디오 피처를 구간화(Binning)하여 이상치의 영향을 줄이고, 모델이 피처간의 비선형적인 관계를 잘 학습할 수 있도록 함

### Focal Loss 적용

정답을 맞히기 쉬운 인기곡 (Easy Sampling)의 비중을 낮추고, 유저의 고유한 취향이 반영된 어려운 샘플 (Hard Sampling)의 Loss를 크게 만들어서 학습의 질 상승

$\text{Focal Loss}(p_t) = -(1 - p_t)^\gamma \log(p_t)$

Why Song Serious 프로젝트에서는 DeepFM의 손실함수로 Focal Loss를 채택해 소수 클래스를 어느정도 보정해줬다.

### 검색 다양성 확보

Faiss 검색 시 입력 곡들의 평균 벡터를 활용하여 계산을 하였지만, 입력 곡이 여러 취향을 담고 있는 경우에 추천 결과에 왜곡이 발생(예, 입력 곡의 tempo가 30,40, 180,170인 경우 평균 tempo벡터는 105).

이후 개별 곡의 벡터도 추가함으로써 유저가 가진 여러 장르적 취향이나 특징을 후보군에 포함 시킬 수 있게 함

# 결과

성능 비교

평가 지표: Recall@10

| DeepFM | LightGCN | EASE |
| --- | --- | --- |
|  0.0191 | 0.2023 | 0.2601 |

# 프로젝트 재현

### Getting Started

- 본 프로젝트는 Docker 환경에서 동작합니다

### Requirements

- Docker & Docker Compose
- PostgresQL

### Repository Clone

```bash
$ git clone https://github.com/boostcampaitech8/pro-recsys-finalproject-recsys-03.git
$ cd pro-recsys-finalproject-recsys-03
```

### Environment Setup (.env)

```bash
$ cp ./backend/.env.example .env
# .env 파일 수정
```

### Run Application

```bash
$ docker-compose up -d
```

## 라이선스 및 출처 표기

### 데이터 (Data)

본 프로젝트는 Kaggle에서 제공되는 **Spotify_1Million_Tracks** 데이터를 활용하였습니다. 해당 데이터는 **Open Data Commons Attribution License (ODC-By) v1.0** 라이선스 규정을 따릅니다.

- **데이터 출처:** https://www.kaggle.com/datasets/amitanshjoshi/spotify-1million-tracks
- **라이선스 상세:** https://opendatacommons.org/licenses/by/1-0/
