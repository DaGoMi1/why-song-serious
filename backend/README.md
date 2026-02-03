# Why Song Serious

음악 취향 기반 탐색 및 시각화 서비스 - Backend API

## 기술 스택

- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL + pgvector
- Poetry

## 시작하기

### 1. 의존성 설치

```bash
pip install poetry
cd ./backend
poetry install
```

### 2. 환경변수 설정

```bash
cp .env.example .env
# .env 파일 수정
```

### 3. 데이터베이스 설정

PostgreSQL에 pgvector 확장 설치:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. 서버 실행

```bash
poetry run uvicorn app.main:app --reload
```

### 5. API 문서 확인

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 프로젝트 구조

```
why-song-serious/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── config.py            # 설정
│   ├── database.py          # DB 연결
│   │
│   ├── auth/                # 인증 (Guest, Spotify OAuth)
│   │
│   ├── domain/              # 도메인별 패키지
│   │   ├── user/
│   │   ├── track/
│   │   ├── playlist/
│   │   ├── preference/
│   │   ├── recommendation/
│   │   ├── interaction/
│   │   └── visualization/
│   │
│   └── common/              # 공통 유틸
│
├── ml_models/               # AI 모델 파일
├── tests/
├── pyproject.toml
└── .env.example
```

## API 엔드포인트

| Method | Endpoint                    | 설명                |
| ------ | --------------------------- | ------------------- |
| POST   | `/api/auth/guest`           | Guest 로그인        |
| GET    | `/api/auth/me`              | 현재 유저 정보      |
| POST   | `/api/tracks/search`        | 취향 기반 트랙 검색 |
| POST   | `/api/interactions/play`    | 트랙 재생 기록      |
| POST   | `/api/interactions/select`  | 트랙 선택 기록      |
| POST   | `/api/recommendations`      | 추천 생성           |
| POST   | `/api/playlists`            | 플레이리스트 생성   |
| GET    | `/api/playlists`            | 플레이리스트 목록   |
| GET    | `/api/visualizations/radar` | 레이더 차트 데이터  |
