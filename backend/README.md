# Why Song Serious

음악 취향 기반 탐색 및 시각화 서비스 - Backend API

## 기술 스택

- Python 3.11
- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL + pgvector
- Alembic (DB 마이그레이션)
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
backend/
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
├── alembic/                 # DB 마이그레이션
│   ├── versions/            # 마이그레이션 파일들
│   └── env.py
│
├── alembic.ini
├── pyproject.toml
└── .env.example
```

## 데이터베이스 마이그레이션

이 프로젝트는 [Alembic](https://alembic.sqlalchemy.org/)을 사용하여 DB 스키마 변경을 관리합니다.

### 처음 설정할 때

**새 DB인 경우** (테이블이 없음):
```bash
alembic upgrade head
```

**기존 DB인 경우** (이미 테이블이 있음):
```bash
# 현재 스키마 상태를 최신 마이그레이션으로 마킹
alembic stamp head
```

### 모델 변경 시 워크플로우

1. **모델 수정** - `app/domain/*/model.py` 파일 수정

2. **마이그레이션 자동 생성**
   ```bash
   alembic revision --autogenerate -m "변경 내용 설명"
   ```

3. **생성된 파일 확인** - `alembic/versions/` 에 생성된 파일의 `upgrade()`, `downgrade()` 함수 검토

4. **마이그레이션 적용**
   ```bash
   alembic upgrade head
   ```

### 자주 쓰는 명령어

| 명령어 | 설명 |
|--------|------|
| `alembic upgrade head` | 모든 마이그레이션 적용 |
| `alembic downgrade -1` | 마지막 마이그레이션 롤백 |
| `alembic current` | 현재 적용된 버전 확인 |
| `alembic history` | 마이그레이션 히스토리 조회 |
| `alembic stamp <revision>` | 실제 실행 없이 버전만 마킹 |

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
| 🔜     | POST   | `/api/interactions/play`       | 트랙 재생 기록    |
| 🔜     | POST   | `/api/interactions/select`     | 트랙 선택 기록    |
| ✅     | POST   | `/api/recommendations`         | 추천 생성         |
| ✅     | GET    | `/api/recommendations/latest`  | 최근 추천 조회    |
| 🔜     | POST   | `/api/playlists`               | 플레이리스트 생성 |
| 🔜     | GET    | `/api/playlists`               | 플레이리스트 목록 |
| 🔜     | GET    | `/api/playlists/{playlist_id}` | 플레이리스트 상세 |

> ✅ 완료 · 🚧 진행 중 · 🔜 후순위
