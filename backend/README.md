# Why Song Serious

음악 취향 기반 탐색 및 시각화 서비스 - Backend API

## 기술 스택

- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL + pgvector
- Alembic (DB 마이그레이션)
- Poetry

## 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 환경에 맞게 수정
```

## 시작하기

### 1. 의존성 설치

```bash
pip install poetry
cd ./backend
poetry install --no-root
```

### 2. DB 마이그레이션

```bash
poetry run alembic upgrade head
```

### 3. 서버 실행

```bash
poetry run uvicorn app.main:app --reload
```

### 4. API 문서 확인

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## 프로젝트 구조

```
backend/
├── alembic/                 # DB 마이그레이션
├── app/
│   ├── auth/                # 인증 (Guest, Spotify OAuth)
│   ├── common/              # 공통 유틸
│   ├── domain/              # 도메인별 패키지
│   │   ├── cluster/
│   │   ├── interaction/
│   │   ├── playlist/
│   │   ├── preference/
│   │   ├── recommendation/
│   │   ├── track/
│   │   └── user/
│   ├── config.py            # 설정
│   ├── database.py          # DB 연결
│   └── main.py              # FastAPI 앱 진입점
├── .env.example
├── alembic.ini
└── pyproject.toml
```

## API 엔드포인트

| Status | Method | Endpoint                       | 설명              |
| ------ | ------ | ------------------------------ | ----------------- |
| ✅     | POST   | `/api/auth/guest`              | Guest 로그인      |
| 🔜     | GET    | `/api/auth/spotify`            | Spotify OAuth     |
| 🔜     | GET    | `/api/auth/spotify/callback`   | Spotify 콜백      |
| ✅     | POST   | `/api/auth/logout`             | 로그아웃          |
| ✅     | GET    | `/api/auth/me`                 | 현재 유저 정보    |
| ✅     | GET    | `/api/preferences/latest`      | 최근 취향 조회    |
| ✅     | POST   | `/api/tracks/search`           | 취향 기반 트랙 검색 |
| ✅     | GET    | `/api/tracks/{track_id}`       | 트랙 상세 조회    |
| ✅     | POST   | `/api/interactions/play`       | 트랙 재생 기록    |
| ✅     | POST   | `/api/recommendations`         | 추천 생성         |
| ✅     | GET    | `/api/recommendations/latest`  | 최근 추천 조회    |
| 🔜     | POST   | `/api/playlists`               | 플레이리스트 생성 |
| 🔜     | GET    | `/api/playlists`               | 플레이리스트 목록 |
| 🔜     | GET    | `/api/playlists/{playlist_id}` | 플레이리스트 상세 |

> ✅ 완료 · 🚧 진행 중 · 🔜 후순위