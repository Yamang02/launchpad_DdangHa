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
# Backend 환경 변수
cp apps/backend/.env.example apps/backend/.env
# 필요시 .env 파일 수정
```

3. **Docker로 전체 스택 실행**
```bash
docker-compose up
```

이 명령으로 다음이 실행됩니다:
- PostgreSQL (포트 5432)
- Backend API (포트 8000)
- Frontend (포트 3000)

4. **개별 실행 (Docker 없이)**

**Backend:**
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
yarn dev
```

**Frontend:**
```bash
cd apps/frontend
yarn install
yarn dev
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

