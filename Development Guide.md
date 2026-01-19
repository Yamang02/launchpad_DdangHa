# Development Guide

## Project Identity

- Repository: launchpad
- Codename: DdangHa
- Team: 땅콩맛 하쿠

---

## Development Rules

1. Specs come first
   - Do not implement features without a spec
   - Specs live in `/docs/specs`

2. Keep domains small
   - One domain should be completable within 1–2 days

3. Prefer clarity over abstraction
   - Builderthon > Perfect architecture

---

## Environment

- Environments: `dev`, `main`
- No real payment, test mode only
- Admin is internal-only

---

## Coding Conventions

프로젝트의 개발 컨벤션은 `/docs/conventions.md`에 정의되어 있습니다.

**주요 컨벤션 영역:**
- **Git 컨벤션**: 브랜치 전략, 커밋 메시지 형식
- **네이밍 컨벤션**: Backend (Python), Frontend (TypeScript/React), Database, API
- **코드 스타일**: 포맷터/린터 설정, 타입 힌팅, Docstring 규칙
- **파일/디렉토리 구조**: Backend 헥사고널 아키텍처, Frontend FSD 구조
- **API 컨벤션**: RESTful 설계, 응답 형식, HTTP 상태 코드
- **에러 처리**: 예외 계층 구조, 에러 핸들링 패턴
- **문서화**: 코드 주석 원칙, API 문서화
- **테스트**: 테스트 작성 가이드라인
- **환경 변수**: 명명 규칙, 관리 방법
- **로깅**: 로깅 레벨 및 형식

> **참고**: 개발 시 반드시 `/docs/conventions.md`를 확인하고 준수하세요.

---

## Testing & TDD

프로젝트에서는 **TDD (Test-Driven Development)** 연습을 권장합니다.

**TDD 가이드:**
- 상세한 TDD 워크플로우는 `/docs/tdd-guide.md`를 참고하세요
- **Frontend**: Playwright를 이용한 E2E 테스트
- **Backend**: pytest를 이용한 API 테스트
- 단계별 연습 시나리오 제공

**빠른 시작:**
```bash
# Frontend E2E 테스트
yarn test:e2e
yarn test:e2e:ui

# Backend 테스트
yarn test:backend
```

---

## 영역별 Skills 참조

프로젝트에서 각 영역을 개발할 때 `.claude/skills/` 아래의 **Skills**를 참고하세요. AI 코딩 도구 사용 시 해당 영역의 skill을 로드해 일관된 품질과 베스트 프랙티스를 적용할 수 있습니다.

| 영역 | Skill | 경로 | 사용 시점 |
|------|-------|------|-----------|
| **Frontend (기능/구조)** | senior-frontend | `.claude/skills/senior-frontend/SKILL.md` | React/Next.js 기능 구현, 성능 최적화, 번들 분석, 컴포넌트 스캐폴딩, 프론트엔드 코드 리뷰 |
| **Frontend (UI/디자인)** | frontend-design | `.claude/skills/frontend-design/SKILL.md` | 페이지·컴포넌트 UI 구성, 비주얼·타이포·컬러·모션 디자인, 제네릭 AI 스타일 회피, 프로덕션 수준 인터페이스 |
| **Backend** | senior-backend | `.claude/skills/senior-backend/SKILL.md` | API 설계·구현, DB 최적화·마이그레이션, 보안·인증/인가, 비즈니스 로직, 백엔드 코드 리뷰 |

**참고 문서 (각 skill 내 `references/`):**

- **senior-frontend**: `react_patterns.md`, `nextjs_optimization_guide.md`, `frontend_best_practices.md`
- **senior-backend**: `api_design_patterns.md`, `database_optimization_guide.md`, `backend_security_practices.md`

> **사용법**: 해당 영역 작업 시 AI에게 “`.claude/skills/senior-frontend/SKILL.md`(또는 해당 skill)를 참고해서 ~”처럼 skill 경로를 명시하면, 스크립트·레퍼런스·워크플로를 활용한 개발이 수월해집니다.

---

## AI Assistance Policy

When using AI coding tools:

- Always reference `DevelopmentGuide.md`
- Always reference the relevant spec
- Always reference `/docs/conventions.md` for coding standards
- Always reference `/docs/tdd-guide.md` for TDD practices
- **영역별로 `.claude/skills/` 내 해당 skill을 참고** (Frontend: senior-frontend, frontend-design / Backend: senior-backend)
- Do not invent requirements
