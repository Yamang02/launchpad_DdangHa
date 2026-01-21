# 테스트 자동화 환경

개발/스테이징 DB와 분리된 **테스트 전용 인프라**에서 자동화된 테스트를 실행하는 방법입니다.

---

## 개요

| 구분 | 개발 환경 | 테스트 (통합 + E2E) |
|------|-----------|----------------------|
| Postgres | `postgres`, 5432, `ddangha_db` | `postgres-test`, **5434**, `ddangha_test` |
| 용도 | dev:backend / dev:frontend | pytest 통합, Playwright E2E (공용) |

**`yarn test:infra:up`** 으로 `postgres-test`(5434)만 기동합니다. 통합 테스트와 E2E가 같은 `ddangha_test`를 씁니다.

---

## 1. 테스트 전용 Postgres 기동

### 로컬: docker-compose up에 포함

```bash
docker compose up -d
# 또는 (백엔드까지 포그라운드)
docker compose up
```

위 명령으로 **postgres**(5432) + **postgres-test**(5434) + **backend**가 모두 올라갑니다. 통합 테스트를 돌리기 전에 추가로 뭔가 띄울 필요 없습니다.

### 테스트 DB만 필요한 경우 (CI 등)

전체 스택 없이 **테스트용 Postgres만** 띄우고 싶을 때:

```bash
yarn test:infra:up
# 또는
docker compose up postgres-test -d
```

중지:

```bash
yarn test:infra:down
# 또는
docker compose stop postgres-test
```

볼륨: `docker volume ls`에서 `postgres_test_data` 확인 후 `docker volume rm <이름>`.

### 테스트 DB 데이터만 비우기 (스키마 유지)

스키마(테이블·인덱스)는 그대로 두고 **데이터만** 지우려면:

```bash
yarn test:db:reset
```

- `TRUNCATE TABLE ... RESTART IDENTITY CASCADE` (public 스키마 전체)
- `postgres-test` 컨테이너가 떠 있어야 함

---

## 2. Backend 테스트

### 환경 변수

- `DATABASE_URL`이 없으면, pytest `conftest`에서  
  `postgresql://...@localhost:5434/ddangha_test` 를 **기본값**으로 사용합니다.
- 다른 호스트/포트/DB를 쓰려면:
  - `apps/backend/env.test.example` 를 참고해 `apps/backend/.env.test` 를 만들거나
  - 셸/CI에서 `DATABASE_URL`을 직접 넘기면 됩니다.

### Unit 테스트 (DB 불필요)

```bash
yarn test:backend:unit
# 또는 apps/backend에서
yarn test:unit
```

Mock만 사용하므로 **테스트용 Postgres를 켤 필요 없습니다.**

### 통합 테스트 (DB 필요)

1. **테스트 DB가 떠 있는지 확인**  
   - `docker compose up`을 했다면 `postgres-test`도 함께 올라가 있음.  
   - 테스트 DB만 쓸 때는 `yarn test:infra:up` 또는 `docker compose up postgres-test -d`.

2. 통합 테스트 실행:

   ```bash
   yarn test:backend:integration
   # 또는 apps/backend에서
   yarn test:integration
   ```

`tests/integration/conftest`가 **session 1회** `alembic upgrade head`를 돌려 `ddangha_test`에 스키마를 맞춥니다. 별도로 `alembic`을 실행할 필요는 없습니다.

### 전체 Backend 테스트

```bash
yarn test:backend
# 또는
yarn test
```

unit + integration이 모두 돌아가며, **`docker compose up`을 해 둔 상태**라면 통합 테스트용 DB도 이미 준비되어 있습니다.

---

## 3. Frontend 테스트

- **Unit (Vitest):** `apps/frontend`에서 `yarn test` / `yarn test:unit` → DB/인프라 없음.
- **E2E (Playwright, 프론트→백엔드→DB):** `yarn test:e2e` → Playwright `webServer`가 **백엔드**(`ddangha_test` 연결)와 **프론트**(Vite)를 둘 다 기동합니다.  
  **선행 조건:** `yarn test:infra:up`으로 `postgres-test`(5434)를 띄워 두어야 합니다.  
  백엔드 DB: `E2E_DATABASE_URL` 미설정 시 `postgresql://...@localhost:5434/ddangha_test` (통합 테스트와 동일).

### 3.1 E2E (프론트-백엔드-DB) 흐름

1. **테스트 DB 기동** (최초 1회 또는 테스트 전)
   ```bash
   yarn test:infra:up
   ```
2. **E2E 실행**
   ```bash
   yarn test:e2e
   ```
   - `scripts/e2e-start-backend.mjs`: `alembic upgrade head` 후 `uvicorn` (포트 8000, **`ddangha_test`** 연결)
   - `yarn dev`: Vite (포트 3000)
   - Playwright: 회원가입 등 e2e 시나리오 실행 (프론트 → API → **ddangha_test**)

**옵션**
- `E2E_DATABASE_URL`: 백엔드가 쓸 DB URL (기본: `...@localhost:5434/ddangha_test`)
- `PYTHON`: `e2e-start-backend`에서 사용할 Python 실행 파일 (기본: `python`)
- 백엔드/프론트가 이미 떠 있으면 `reuseExistingServer`로 재사용 (CI 제외)

---

## 4. 스크립트 요약 (루트)

| 스크립트 | 설명 |
|----------|------|
| `yarn test` | `yarn test:backend` (unit + integration) |
| `yarn test:backend` | Backend pytest 전체 |
| `yarn test:backend:unit` | Backend unit만 |
| `yarn test:backend:integration` | Backend integration만 (`docker compose up` 또는 `test:infra:up`으로 테스트 DB 준비) |
| `yarn test:infra:up` | 테스트용 Postgres 기동: `postgres-test`(5434) |
| `yarn test:infra:down` | 테스트용 Postgres 중지 |
| `yarn test:db:reset` | 테스트 DB 데이터만 삭제 (스키마 유지, `ddangha_test`) |
| `yarn test:e2e` | Playwright E2E (프론트+백엔드+DB, webServer가 둘 다 기동). **선행:** `yarn test:infra:up` |
| `yarn test:e2e:ui` | Playwright UI 모드 (테스트 선택·실행·결과·trace를 브라우저에서) |
| `yarn test:e2e:report` | 마지막 E2E 실행의 HTML 리포트를 브라우저로 열기 (`yarn test:e2e` 실행 후 사용) |
| `yarn test:frontend:unit:ui` | Vitest UI 모드 (Unit 테스트를 브라우저에서 실행·확인) |

---

## 5. 테스트 결과 GUI / 리포트

| 대상 | 방법 | 명령 |
|------|------|------|
| **Playwright E2E** | **UI 모드** (테스트 선택, 실행, trace, 스크린샷 등) | `yarn test:e2e:ui` |
| **Playwright E2E** | **HTML 리포트** (마지막 실행 결과) | `yarn test:e2e` 실행 후 `yarn test:e2e:report` |
| **Vitest Unit** | **UI 모드** (테스트 목록, 실행, 결과) | `yarn test:frontend:unit:ui` (또는 `apps/frontend`에서 `yarn test:unit:ui`) |
| **pytest (Backend)** | **커버리지 HTML** (라인 커버리지 + 결과) | `cd apps/backend && yarn test:cov` 후 `htmlcov/index.html` 브라우저로 열기 |

---

## 6. CI에서 사용할 때

1. `docker compose up postgres-test -d` 로 테스트용 Postgres 기동 (5434/ddangha_test).
2. `DATABASE_URL=postgresql://...@localhost:5434/ddangha_test` (또는 CI 호스트/포트). E2E도 동일 DB, `E2E_DATABASE_URL`로 덮어쓸 수 있음.
3. `yarn test:backend` 또는 `pytest -m "unit or integration"` 실행.  
   `conftest`의 `setdefault` 때문에 `DATABASE_URL`이 없을 때만 `localhost:5434/ddangha_test`가 붙고, CI에서 이미 넣어주면 그 값을 사용합니다.

Docker-in-Docker나 `services:` 로 Postgres를 쓰는 경우, `DATABASE_URL`의 호스트만 `postgres-test` 등 서비스 이름으로 바꿔주면 됩니다.

---

## 7. 트러블슈팅

- **`connection refused` / `could not connect to server`**  
  - `yarn test:infra:up` 후 `docker compose ps`로 `postgres-test`가 `Up (healthy)`인지 확인. `DATABASE_URL` 포트 **5434** / `ddangha_test`.
- **`relation "users" does not exist`**  
  - 통합 테스트의 `migrate_test_db` 픽스처가 `alembic upgrade head`를 실행합니다.  
  - `alembic.ini`가 `apps/backend`에 있고, pytest를 **`apps/backend` 기준**으로 실행하는지 확인 (보통 `yarn workspace @ddangha/backend test` 이면 됨).
- **Unit만 돌리는데 `DATABASE_URL`/DB 에러가 나는 경우**  
  - `conftest`에서 `setdefault`로 테스트 DB URL을 넣지만, **실제 접속**은 통합 테스트에서만 일어납니다.  
  - `from main import app` 시점에 `database` 모듈이 로드되므로, `DATABASE_URL` 형식이 잘못되면 import 단계에서 에러가 날 수 있습니다.  
  - `yarn test:unit`만 쓸 때는 `.env.test`에 `DATABASE_URL`을 두지 않고, `conftest` 기본값 `localhost:5434`를 쓰거나, 아예 사용하지 않는 존재하는 DB URL을 두어도 됩니다. Unit은 mock만 사용하므로 해당 DB에 연결되지는 않습니다.

- **E2E: `relation "users" does not exist` / `alembic` 실패**  
  - `e2e-start-backend.mjs`가 `alembic upgrade head`를 `ddangha_test`에 실행합니다. `postgres-test`가 `Up (healthy)`인지, `E2E_DATABASE_URL`(또는 기본값)이 `localhost:5434`/`ddangha_test`인지 확인하세요.

- **E2E: `python`/`alembic`/`uvicorn`을 찾을 수 없음**  
  - 백엔드 의존성 설치: `cd apps/backend && pip install -e ".[dev]"` (가상환경 사용 시 활성화 후).  
  - `PYTHON`으로 실행 파일 지정: `PYTHON=python3 yarn test:e2e` (또는 해당 가상환경의 `python` 경로).

---

## 참고

- Backend/Frontend TDD 흐름: [tdd-guide.md](tdd-guide.md)
- 회원가입 API 스펙/검증: [spec/01-user-auth/001-signup-design.md](spec/01-user-auth/001-signup-design.md)
