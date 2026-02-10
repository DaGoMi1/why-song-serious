# README 작성

---

# 🎵 **Why Song Serious?**

---

왜 이 음악이 추천되었을까요?

취향을 기반으로 음악을 탐색하고 시각화하는 서비스입니다!

![프로젝트 시현.gif](attachment:e538d999-afec-428b-8d09-635c9ac49d9d:프로젝트_시현.gif)

# 😀 팀 소개

| 구승민 | 박주연 | 송정호 | 이다검 | 이성재 | 최연우 |
| --- | --- | --- | --- | --- | --- |
| <a href = 'https://github.com/gsmin02'><img  width="100" height="100" src = 'https://avatars.githubusercontent.com/u/86878502?v=4'></a> | <a href = 'https://github.com/wndus0212'><img  width="100" height="100" src = 'https://avatars.githubusercontent.com/u/83656909?v=4'></a> | <a href = 'https://github.com/dynamite885'><img  width="100" height="100" src = 'https://avatars.githubusercontent.com/u/50672132?v=4'></a> | <a href = 'https://github.com/DaGoMi1'><img  width="100" height="100" src = 'https://avatars.githubusercontent.com/u/155869202?v=4'></a> | <a href = 'https://github.com/localman211'><img  width="100" height="100" src = 'https://avatars.githubusercontent.com/u/223304427?v=4'></a> | <a href = 'https://github.com/Choiyeonw00'><img  width="100" height="100" src = 'https://avatars.githubusercontent.com/u/105337438?v=4'></a> |

# 역할 분배

| **구승민** | **박주연** | **송정호** | **이다검** | **이성재** | **최연우** |
| --- | --- | --- | --- | --- | --- |
|   • AWS EC2 서버 구축 |   • EDA |   • Backend |   • Modeling - Faiss & DeepFM |   • Modeling - CML, EASE |   • Modeling - LightGCN |
|   • 배포 자동화 구축 |   • Frontend |   • ERD 설계 |   • Model Serving |   • clustering |  • EDA |
|   • GitHub 관리 |  |  |  |  |   • LLM 기반 설명 설계 |

# 프로젝트 타임라인

| 날짜 (2026) | 내용 |
| --- | --- |
| 1/16 | 아이디어 선정, 핵심 기능 선정 |
| 1/20 | 유저 시나리오 정리 |
| 1/22 | 와이어프레임, 플로우차트, ERD, API 명세 작성 |
| 1/27 | 데이터셋 및 평가지표 선정 |
| 1/29 | 프론트 디자인 제작, EC2 서버 구축 |
| 1/30 | 데드라인 설정, 데이터 전달 형식 동기화 |
| 2/2 | 학습 모델 테스트, 프론트 및 백엔드 연동 |
| 2/3 | 프로토타입 서빙, 추천 곡 목록 수 지정 |
| 2/4 | 모델 입력 구조 변경, 클러스터 기능 구현 |
| 2/5 | CI/CD 구축 완료, DB 데이터 업로드 및 클러스터 적용 |
| 2/6 | 서비스 모델 서빙, 발표자료 작성, 프로젝트 완성 |

# **🛠️**기술 스택

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=Python&logoColor=white"> <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=React&logoColor=white"> <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white"> <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=PyTorch&logoColor=white"> <img src="https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white">  <img src="[https://img.shields.io/badge/Amazon EC2-FF9900?style=for-the-badge&logo=Amazon EC2&logoColor=white](https://img.shields.io/badge/Amazon%20EC2-FF9900?style=for-the-badge&logo=Amazon%20EC2&logoColor=white)"> <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=PostgreSQL&logoColor=white"> <img src="https://img.shields.io/badge/nginx-%23009639.svg?style=for-the-badge&logo=nginx&logoColor=white">

# 주요 구현 기능

1. 오디오 피처 슬라이더를 유저가 오디오 피쳐 선택
2. 후보군 음악 PGVector 검색 및 유저 노출
3. 곡 선택
4. 선택된 곡들을 입력으로 넣어 Faiss 검색과 DeepFM two-stage 방식으로 플레이리스트 생성
5. 생성된 플레이리스트 기반으로 레이더차트와 클러스터맵 생성

# 아키텍처

### 서비스 아키텍처

![image.png](attachment:6a49d2f5-fe10-4886-a0bc-ca9ef793461b:image.png)

### 모델 아키텍처

![image.png](attachment:a74e7308-dbbd-44ec-a373-3326919e64f3:image.png)

### 설명 가능성 알고리즘

![image.png](attachment:39dbe90a-6f63-4afc-8846-3b844eb5bfe1:image.png)

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
