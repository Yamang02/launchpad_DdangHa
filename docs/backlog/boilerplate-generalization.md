# 보일러플레이트 범용화 백로그

> Design: [001-dockerize-design.md](../infra/001-dockerize-design.md)

이 문서는 DdangHa 프로젝트를 **보편적 프로젝트 보일러플레이트**로 전환하기 위해 필요한 작업 목록이다.

---

## 1. Docker / 인프라

### 1.1 docker-compose.yml
- [ ] frontend 서비스 추가 (Dockerfile은 이미 존재)
- [ ] 환경변수 하드코딩 제거 → `env_file` 방식으로 전환
- [ ] 명시적 네트워크 정의 추가
- [ ] backend, frontend에 healthcheck 추가

### 1.2 Backend Dockerfile
- [ ] `pip install` 나열 방식 제거 → `pip install .` 또는 `pip install -e .`로 pyproject.toml 활용
- [ ] 누락 패키지 확인 (`pyjwt` 등)
- [ ] Multi-stage build 적용 (builder → runtime 분리, 이미지 크기 최적화)
- [ ] `--reload` 플래그는 dev용 compose override로 분리
- [ ] `.dockerignore` 추가 (`__pycache__`, `.venv`, `tests/`, `.git`, `*.pyc` 등)

### 1.3 Frontend Dockerfile
- [ ] Multi-stage build 적용 (build stage → nginx 서빙)
- [ ] Production 빌드 지원 (`yarn build` → nginx로 정적 파일 서빙)
- [ ] `.dockerignore` 추가 (`node_modules`, `dist`, `.git` 등)

### 1.4 환경변수 관리
- [ ] `apps/backend/.env.example` 정비 (모든 필수 환경변수 placeholder 포함)
- [ ] `apps/frontend/.env.example` 생성 (`VITE_API_URL` 등)
- [ ] `.env.example` → `.env` 복사 과정을 README에 명시

### 1.5 dev/prod 분리
- [ ] `docker-compose.yml` — production 기본값
- [ ] `docker-compose.override.yml` — dev 전용 설정 (volume mount, --reload, 소스 마운트 등)

---

## 2. 프로젝트 네이밍 범용화

현재 `ddangha`, `DdangHa`, `땅콩맛 하쿠` 등 팀 고유 명칭이 곳곳에 박혀 있다.
보일러플레이트로 배포하려면 이를 제거하거나 placeholder로 교체해야 한다.

### 대상 파일 목록
- [ ] `README.md` — "FastCampus Builderthon 2026", "땅콩맛 하쿠 팀", "Codename: DdangHa" 제거
- [ ] `docs/architecture.md` — "DdangHa" 언급 제거, 빌더톤 전제 문구 범용화
- [ ] `docs/tech-stack.md` — "launchpad (DdangHa)" → 프로젝트명 placeholder, 빌더톤 맥락 제거
- [ ] `docs/conventions.md` — "빌더톤 환경에 맞춰" 문구 범용화
- [ ] `docker-compose.yml` — 컨테이너명, DB명, 유저명 등을 범용 명칭으로 변경
- [ ] `apps/backend/` — 코드 내 `ddangha` 참조 검색 후 교체
- [ ] `package.json` (root) — 프로젝트명 확인 및 교체

---

## 3. 문서 범용화

### 3.1 README.md
- [ ] "빌더톤/해커톤" 맥락 제거
- [ ] 프로젝트 설명을 "FastAPI + React + PostgreSQL 모노레포 보일러플레이트"로 변경
- [ ] Quick Start 가이드 정비 (clone → env 설정 → docker compose up → 완료)
- [ ] 포함된 기능 목록 정리 (인증, API 구조, 테스트 환경 등)
- [ ] "이 보일러플레이트를 사용하는 법" 섹션 추가

### 3.2 docs/architecture.md
- [ ] "빌더톤과 같은 단기간 개발 환경을 전제" → "범용적인 웹 프로젝트를 전제"로 변경
- [ ] "무박 2일 환경에서도 빠른 구현과 수정" → "빠른 구현과 수정이 가능한 구조"
- [ ] AWS Lambda 전제를 선택 사항으로 변경 (Docker 배포도 가능하도록)

### 3.3 docs/tech-stack.md
- [ ] 기술 선택 이유에서 빌더톤 맥락 제거
- [ ] "Django: 과도한 기능, 빌더톤에 무거움" → "Django: 이 템플릿의 경량 설계 의도와 맞지 않음" 등으로 변경
- [ ] 배포 옵션을 Lambda 단독이 아닌 Docker/Lambda/VPS 선택 가능으로 기술

### 3.4 docs/conventions.md
- [ ] "빌더톤 기간에는 복잡한 브랜치 전략 지양" → 범용적 브랜치 전략으로 변경
- [ ] "빌더톤 환경에 맞춰 실용적이고 간단한 규칙" → "실용적이고 간단한 규칙"

### 3.5 기타 docs
- [ ] `docs/epic/01-user-auth/planning.md` — 빌더톤 맥락 확인 및 정리
- [ ] `docs/spec/` 내 문서들 — 예시 스펙으로서 유지하되, 팀 고유 맥락 제거
- [ ] `Development Guide.md` — 빌더톤 맥락 확인 및 정리

---

## 4. 코드 정리

### 4.1 브랜치 작업 정리
- [ ] 현재 `spec/01-user-auth/002-login` 브랜치 작업 완료 후 main에 머지
- [ ] 인증 기능은 보일러플레이트에 **포함** (예시 기능으로 유지)

### 4.2 테스트 DB
- [ ] `postgres-test` 서비스를 **optional**로 변경 (별도 profile 또는 compose 파일로 분리)

---

## 5. CI/CD

현재 이 프로젝트는 어디에도 배포되지 않은 상태이며, 프로젝트에 따라 다른 인프라를 사용할 수 있도록 할 예정이다.

- [ ] GitHub Actions 워크플로우 — 테스트 자동화만 우선 구성
- [ ] 배포 워크플로우는 **인프라 선택 후 별도 구성** (Docker/Lambda/VPS 등 프로젝트에 따라 다름)
- [ ] 배포 관련 문서에 "인프라별 배포 가이드 placeholder" 추가

---

## 작업 우선순위

1. **네이밍 범용화** (ddangha → 범용 명칭)
2. **Docker 정비** (compose, Dockerfile, .dockerignore, env 관리)
3. **문서 범용화** (README, architecture, tech-stack, conventions)
4. **코드/브랜치 정리**
5. **CI/CD 정비**
