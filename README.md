# launchpad

Spec-driven monorepo for rapid service building.

FastCampus Builderthon 2026  
Codename: **DdangHa**  
by **땅콩맛 하쿠 팀**

---

## Overview

`launchpad` is a reusable monorepo template designed for:

- Rapid development in short-term competitions (e.g. builderthon, hackathon)
- Long-term reuse as a personal/team baseline
- AI-assisted, spec-driven development
- Low-cost, scalable infrastructure (serverless-first)

This repository is **not tied to a specific service idea**.

---

## Core Principles

- **Spec First**
  - Specs are written before implementation
  - Code must follow the specs in `/docs/specs`

- **Simple by Default**
  - Avoid premature abstraction
  - One domain = one clear responsibility

- **Builderthon-friendly**
  - Fast local development
  - Minimal infra setup
  - Easy onboarding for junior teammates

---

## Tech Stack (Initial)

### Backend
- FastAPI
- AWS Lambda + API Gateway (planned)
- Railway (DB)
- In-memory / optional cache abstraction

### Frontend
- React + TypeScript
- Feature-Sliced Design (FSD)

### Infra & Tooling
- Docker (local development)
- GitHub Actions (CI)
- Monorepo (yarn workspaces)

---

## Project Structure

```text
apps/        # runnable applications
packages/    # shared code
docs/        # specs & architecture
infra/       # infrastructure-related files
```

---

## 로컬 개발환경 설정

### 사전 요구사항

- Node.js >= 18.0.0
- Yarn >= 1.22.0
- Python >= 3.11
- Docker & Docker Compose

### 설치 및 실행

1. **의존성 설치**
```bash
yarn install
```

2. **환경 변수 설정**
```bash
# Backend 환경 변수 (로컬에서 백엔드 실행 시)
cp apps/backend/env.example apps/backend/.env
# 필요시 .env 파일 수정
```

3. **Docker로 Postgres + Backend 실행**
```bash
docker-compose up
```

이 명령으로 다음이 실행됩니다:
- **PostgreSQL** (호스트 포트 5432, DB: `ddangha_db`)
- **Backend API** (포트 8000, 기동 시 `alembic upgrade head` 자동 실행)

Frontend는 HMR·환경 변수 편의를 위해 **로컬에서 실행**합니다.

4. **Frontend 로컬 실행**
```bash
cd apps/frontend
yarn install
yarn dev
```

- Vite 기본: `http://localhost:5173` (vite.config에 `port: 3000`이면 3000)
- API: `http://localhost:8000/api/v1` (백엔드 Docker 기동 시)

5. **DB 클라이언트 접속 (DBeaver, pgAdmin 등)**

| 항목 | 값 |
|------|-----|
| Host | `localhost` |
| Port | `5432` |
| Database | `ddangha_db` |
| User | `ddangha_user` |
| Password | `ddangha_password` |

> `docker-compose up`으로 Postgres가 떠 있어야 합니다. 다른 프로젝트가 5432를 쓰면 포트가 겹치므로, 동시에 하나만 실행하세요.

6. **Backend만 로컬 실행 (Docker Postgres 연결)**

Docker Postgres는 띄운 상태에서:
```bash
cd apps/backend
# pip install -e ".[dev]"  # 최초 1회
$env:DATABASE_URL="postgresql://ddangha_user:ddangha_password@localhost:5432/ddangha_db"  # PowerShell
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 개발 스크립트

```bash
# Backend 개발 서버
yarn dev:backend

# Frontend 개발 서버
yarn dev:frontend

# 전체 빌드
yarn build

# 타입 체크
yarn type-check
```

---

## How to Start

> Detailed instructions are in `DevelopmentGuide.md`

1. Read the specs in `/docs/specs`
2. Follow the rules defined in `DevelopmentGuide.md`
3. Implement features based on specs

---

## Codename: DdangHa

`DdangHa` is the internal codename for this project.

* Used as a prefix for services, resources, and internal naming
* Represents the team identity of **땅콩맛 하쿠**

---

## License

MIT

