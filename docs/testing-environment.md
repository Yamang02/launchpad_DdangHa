# 테스트 자동화 환경

개발/스테이징 DB와 분리된 **테스트 전용 인프라**에서 자동화된 테스트를 실행하는 방법입니다.

---

## 개요

| 구분 | 개발 환경 | 테스트 환경 |
|------|-----------|-------------|
| Postgres | `ddangha-postgres`, 포트 5432, DB `ddangha_db` | `ddangha-postgres-test`, 포트 **5434**, DB `ddangha_test` |
| 용도 | `dev:backend` / `dev:frontend` | pytest 통합 테스트, (선택) E2E |

**`docker-compose up`** 하면 개발용 Postgres(`postgres`)와 테스트용 Postgres(`postgres-test`)가 **함께** 기동됩니다. 별도로 테스트 DB만 띄울 필요 없습니다.

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

볼륨까지 지우려면 `docker volume ls`로 `postgres_test`가 포함된 이름을 찾아 `docker volume rm <이름>` 하면 됨.

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
- **E2E (Playwright):** `yarn test:e2e` → `playwright.config`의 `webServer`로 프론트를 띄우고, **백엔드 API는 별도로** `yarn dev:backend` 등으로 `localhost:8000`에 띄워 두어야 합니다.  
  E2E에서 백엔드를 테스트 DB에 붙이려면, 백엔드 기동 시 `DATABASE_URL=...@localhost:5434/ddangha_test` 로 실행하면 됩니다.

---

## 4. 스크립트 요약 (루트)

| 스크립트 | 설명 |
|----------|------|
| `yarn test` | `yarn test:backend` (unit + integration) |
| `yarn test:backend` | Backend pytest 전체 |
| `yarn test:backend:unit` | Backend unit만 |
| `yarn test:backend:integration` | Backend integration만 (`docker compose up` 또는 `test:infra:up`으로 테스트 DB 준비) |
| `yarn test:infra:up` | 테스트용 Postgres만 기동 (CI 등, `docker compose up postgres-test -d`) |
| `yarn test:infra:down` | 테스트용 Postgres만 중지 (`docker compose stop postgres-test`) |
| `yarn test:e2e` | Frontend Playwright E2E |

---

## 5. CI에서 사용할 때

1. `docker compose up postgres-test -d` 로 테스트용 Postgres 기동.
2. `DATABASE_URL=postgresql://ddangha_user:ddangha_password@localhost:5434/ddangha_test` (또는 CI가 제공하는 호스트/포트) 를 환경 변수로 설정.
3. `yarn test:backend` 또는 `pytest -m "unit or integration"` 실행.  
   `conftest`의 `setdefault` 때문에 `DATABASE_URL`이 없을 때만 `localhost:5434/ddangha_test`가 붙고, CI에서 이미 넣어주면 그 값을 사용합니다.

Docker-in-Docker나 `services:` 로 Postgres를 쓰는 경우, `DATABASE_URL`의 호스트만 `postgres-test` 등 서비스 이름으로 바꿔주면 됩니다.

---

## 6. 트러블슈팅

- **`connection refused` / `could not connect to server`**  
  - `docker compose up` 또는 `yarn test:infra:up` 후 `docker compose ps`로 `postgres-test`가 `Up (healthy)`인지 확인.
  - `DATABASE_URL` 포트가 **5434**인지 확인 (기본값).
- **`relation "users" does not exist`**  
  - 통합 테스트의 `migrate_test_db` 픽스처가 `alembic upgrade head`를 실행합니다.  
  - `alembic.ini`가 `apps/backend`에 있고, pytest를 **`apps/backend` 기준**으로 실행하는지 확인 (보통 `yarn workspace @ddangha/backend test` 이면 됨).
- **Unit만 돌리는데 `DATABASE_URL`/DB 에러가 나는 경우**  
  - `conftest`에서 `setdefault`로 테스트 DB URL을 넣지만, **실제 접속**은 통합 테스트에서만 일어납니다.  
  - `from main import app` 시점에 `database` 모듈이 로드되므로, `DATABASE_URL` 형식이 잘못되면 import 단계에서 에러가 날 수 있습니다.  
  - `yarn test:unit`만 쓸 때는 `.env.test`에 `DATABASE_URL`을 두지 않고, `conftest` 기본값 `localhost:5434`를 쓰거나, 아예 사용하지 않는 존재하는 DB URL을 두어도 됩니다. Unit은 mock만 사용하므로 해당 DB에 연결되지는 않습니다.

---

## 참고

- Backend/Frontend TDD 흐름: [tdd-guide.md](tdd-guide.md)
- 회원가입 API 스펙/검증: [spec/01-user-auth/001-signup-design.md](spec/01-user-auth/001-signup-design.md)
