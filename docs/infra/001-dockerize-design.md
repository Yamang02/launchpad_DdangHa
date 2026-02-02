# 001-dockerize 구현 설계 문서

> Backlog: [boilerplate-generalization.md](../backlog/boilerplate-generalization.md)
> Branch: `infra/001-dockerize`

---

## 1. 목적

프로젝트를 보편적 보일러플레이트로 사용할 수 있도록 Docker 환경을 정비한다.

- `docker compose up` 한 번으로 전체 스택(DB + Backend + Frontend) 실행
- dev/prod 환경 분리
- 환경변수를 `.env` 파일로 외부화
- 이미지 크기 최적화 (multi-stage build)

---

## 2. 현재 상태

| 항목 | 상태 | 문제 |
|------|------|------|
| `docker-compose.yml` | postgres + backend만 등록 | frontend 미등록 |
| Backend Dockerfile | 존재 | ~~pip install 나열 방식, pyproject.toml 미활용, pyjwt 누락~~ → 해결됨 |
| Frontend Dockerfile | 존재 | dev 모드 전용, production build 미지원 |
| `.dockerignore` | 없음 | 불필요한 파일이 이미지에 포함 |
| 환경변수 | compose에 하드코딩 | env_file 미사용 |
| dev/prod 분리 | 없음 | 단일 compose 파일 |

---

## 3. 구현 체크리스트

### Phase 1: .dockerignore 추가

- [x] `apps/backend/.dockerignore`
  ```
  __pycache__/
  *.pyc
  .venv/
  .env
  .git/
  tests/
  .pytest_cache/
  .mypy_cache/
  .ruff_cache/
  ```
- [x] `apps/frontend/.dockerignore`
  ```
  node_modules/
  dist/
  .git/
  .env
  .env.local
  coverage/
  e2e/
  ```

### Phase 2: Backend Dockerfile 개선

- [x] Multi-stage build 적용
- [x] `pyproject.toml` 기반 의존성 설치 (`pip install .`)
- [x] Production CMD: `uvicorn main:app --host 0.0.0.0 --port 8000` (--reload 없음)

### Phase 3: Frontend Dockerfile 개선

- [x] Multi-stage build 적용 (build → nginx)
- [x] Production: nginx로 정적 파일 서빙
- [x] nginx.conf 작성 (SPA fallback, API proxy)

### Phase 4: 환경변수 외부화

- [x] `apps/backend/.env.example` 정비
- [x] `apps/frontend/.env.example` 생성
- [x] docker-compose에서 `env_file` 사용

### Phase 5: docker-compose.yml 정비

- [x] frontend 서비스 추가
- [x] 네트워크 명시적 정의
- [x] backend, frontend healthcheck 추가
- [x] `postgres-test`를 profiles로 optional 처리

### Phase 6: dev/prod 분리

- [x] `docker-compose.yml` — production 기본값
- [x] `docker-compose.override.yml` — dev 전용 (volume mount, --reload 등)

---

## 4. 상세 설계

### 4.1 Backend Dockerfile (Multi-stage)

```dockerfile
# ===== Builder =====
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# ===== Runtime =====
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4.2 Frontend Dockerfile (Multi-stage)

yarn workspaces 모노레포 — build context는 프로젝트 root.

```dockerfile
# ===== Build =====
FROM node:18-alpine AS builder

WORKDIR /app

COPY package.json yarn.lock ./
COPY apps/frontend/package.json ./apps/frontend/
RUN yarn install --frozen-lockfile

COPY apps/frontend ./apps/frontend
WORKDIR /app/apps/frontend
RUN yarn build

# ===== Runtime =====
FROM nginx:alpine

RUN apk add --no-cache curl

COPY --from=builder /app/apps/frontend/dist /usr/share/nginx/html
COPY apps/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### 4.3 nginx.conf (Frontend)

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (production에서는 별도 설정 가능)
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 4.4 docker-compose.yml (Production 기본값)

```yaml
services:
  postgres:
    image: postgres:15-alpine
    container_name: app-postgres
    env_file:
      - ./apps/backend/.env
    environment:
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
      LANG: "C.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - app-network

  postgres-test:
    image: postgres:15-alpine
    container_name: app-postgres-test
    profiles:
      - test
    environment:
      POSTGRES_USER: app_user
      POSTGRES_PASSWORD: app_password
      POSTGRES_DB: app_test
      POSTGRES_INITDB_ARGS: "--encoding=UTF8"
      LANG: "C.UTF-8"
    ports:
      - "5434:5432"
    volumes:
      - postgres_test_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app_user -d app_test"]
      interval: 5s
      timeout: 3s
      retries: 5
    networks:
      - app-network

  backend:
    build:
      context: ./apps/backend
      dockerfile: Dockerfile
    container_name: app-backend
    ports:
      - "8000:8000"
    env_file:
      - ./apps/backend/.env
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

  frontend:
    build:
      context: .
      dockerfile: apps/frontend/Dockerfile
    container_name: app-frontend
    ports:
      - "3000:80"
    depends_on:
      backend:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

volumes:
  postgres_data:
  postgres_test_data:

networks:
  app-network:
    driver: bridge
```

### 4.5 docker-compose.override.yml (Dev 전용)

`docker compose up` 시 자동으로 merge된다.

```yaml
services:
  backend:
    volumes:
      - ./apps/backend:/app
    command: sh -c "(alembic upgrade head 2>/dev/null || true) && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

  frontend:
    build:
      context: .
      dockerfile: apps/frontend/Dockerfile.dev
    volumes:
      - ./apps/frontend:/app/apps/frontend
      - /app/node_modules
    ports:
      - "3000:3000"
    command: yarn dev --host 0.0.0.0
```

> **참고**: dev용 frontend는 별도 `Dockerfile.dev` (node만 있는 단순 이미지)를 사용하거나,
> 기존 Dockerfile의 builder stage만 사용할 수 있다.

### 4.6 환경변수 파일

**`apps/backend/.env.example`**:
```env
# Database
POSTGRES_USER=app_user
POSTGRES_PASSWORD=app_password
POSTGRES_DB=app_db
DATABASE_URL=postgresql+asyncpg://app_user:app_password@postgres:5432/app_db

# Security
JWT_SECRET_KEY=your-secret-key-minimum-32-bytes-change-this
BCRYPT_ROUNDS=12

# Server
ENV=dev
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

**`apps/frontend/.env.example`**:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 5. 실행 방법

### 사전 준비
```bash
# docker-compose 변수 치환용 (postgres healthcheck 등)
cp .env.example .env

# 컨테이너 env
cp apps/backend/.env.example apps/backend/.env

# 필요시 .env 파일 수정 (POSTGRES_USER, POSTGRES_PASSWORD 등)
# root .env와 apps/backend/.env의 POSTGRES_USER, POSTGRES_DB는 동일하게 유지
```

### Production 모드
```bash
docker compose up --build
```
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- PostgreSQL: `localhost:5432`

### Dev 모드 (override 자동 적용)
```bash
docker compose up --build
```
- override 파일이 있으면 자동으로 merge
- volume mount로 hot reload 지원

### 테스트 DB 포함 실행
```bash
docker compose --profile test up
```

---

## 6. 디렉터리 구조 (완료 시)

```
project-root/
├── docker-compose.yml              # production 기본값
├── docker-compose.override.yml     # dev 전용 (자동 merge)
├── .env.example                   # compose 변수 치환용 (POSTGRES_USER, POSTGRES_DB)
├── apps/
│   ├── backend/
│   │   ├── Dockerfile              # multi-stage (builder → runtime)
│   │   ├── .dockerignore
│   │   ├── .env.example
│   │   └── ...
│   └── frontend/
│       ├── Dockerfile              # multi-stage (build → nginx)
│       ├── Dockerfile.dev          # dev 전용 (optional)
│       ├── nginx.conf
│       ├── .dockerignore
│       ├── .env.example
│       └── ...
└── docs/
    ├── backlog/
    │   └── boilerplate-generalization.md
    └── infra/
        └── 001-dockerize-design.md
```

---

## 7. 참조 문서

- [Backlog](../backlog/boilerplate-generalization.md) — 전체 범용화 작업 목록
- [Architecture](../architecture.md) — 아키텍처 개요
- [Tech Stack](../tech-stack.md) — 기술 스택
