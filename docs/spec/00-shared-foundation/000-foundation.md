# 000-shared-foundation 스펙

> 001-signup 구현 전 공통 인프라. TDD(Red → Green → Refactor)로 진행.
> Branch: `spec/00-shared-foundation`

---

## 1. 목적

001-signup 및 이후 기능에서 공통으로 사용할 다음을 선구현한다.

| # | 항목 | Backend | Frontend |
|---|------|---------|----------|
| 1 | **아이디 생성 (UID)** | `shared/uid.py` (ULID+prefix) | - |
| 2 | **시간 처리** | - | `shared/lib/date.ts` (`formatToKST`) |
| 3 | **API 표준화** | 공통 response/error 스키마, 표준 라우트 예시 | `api/client`, `types/api`, `api/errors` |

---

## 2. TDD 체크리스트 (RED → Green → Refactor)

### 2.1 Backend

#### 2.1.1 UID (`app/shared/uid.py`)

- [x] **RED** `tests/unit/shared/test_uid.py`
  - [x] `generate_uid(prefix)` → `{prefix}{ULID 26자}` 형식, prefix 포함
  - [x] `generate_user_uid()` → `"usr_"` prefix
  - [x] ULID 26자 정규 `[0-9A-HJKMNP-TV-Z]{26}`
- [x] **GREEN** `app/shared/uid.py` + `python-ulid` 의존성
- [ ] **Refactor** (필요 시)

#### 2.1.2 API 공통 Response 스키마 (`app/shared/schemas/response.py`)

- [x] **RED** `tests/unit/shared/test_response_schemas.py`
  - [x] `ApiSuccessResponse[data].model_dump()` → `{"success": True, "data": data}`
  - [x] `ApiErrorResponse(error=...).model_dump()` → `{"success": False, "error": {code, message, details?}}`
- [x] **GREEN** `app/shared/schemas/response.py` (Pydantic)
- [ ] **Refactor** (필요 시)

#### 2.1.3 API 표준 형식 통합 검증 (라우트 + 에러 형식)

- [ ] **RED** `tests/integration/test_api_standard_response.py`
  - [ ] `GET /api/v1/_spec/ok` → 200, `success` True, `data` 존재
  - [ ] `GET /api/v1/_spec/error` → 400, `success` False, `error.code`, `error.message`
- [ ] **GREEN** `_spec` 라우터, `main`에 등록, 스키마/에러핸들러 연동
- [ ] **Refactor** (필요 시)

---

### 2.2 Frontend

#### 2.2.1 시간 유틸 (`shared/lib/date.ts`)

- [ ] **RED** `src/shared/lib/date.test.ts`
  - [ ] `formatToKST("2025-01-19T15:30:00Z")` → KST `"2025. 01. 20. 00:30"` 형식
  - [ ] `formatToKST("2025-01-19T15:30:00.000Z")` → 동일
- [ ] **GREEN** `src/shared/lib/date.ts` (Intl + `Asia/Seoul`)
- [ ] **Refactor** (필요 시)

#### 2.2.2 API 에러 변환 (`shared/api/errors.ts`)

- [ ] **RED** `src/shared/api/errors.test.ts`
  - [ ] `toApiError(axiosError)` when `response.data.error` 있음 → `{ code, message }` (및 `details`)
  - [ ] `toApiError(axiosError)` when `response` 없음 → `{ code: "UNKNOWN_ERROR", message: "알 수 없는 오류..." }`
- [ ] **GREEN** `src/shared/api/errors.ts`, `shared/types/api.ts` (`ApiError`)
- [ ] **Refactor** (필요 시)

#### 2.2.3 API 클라이언트 / 타입 (Green 시 client에 toApiError 연동)

- [ ] **GREEN** `src/shared/api/client.ts` (baseURL, 에러 인터셉터에서 `toApiError` 사용)
- [ ] **GREEN** `src/shared/types/api.ts` (`ApiResponse<T>`, `ApiError`)

---

## 3. 디렉터리 구조 (완료 시)

```
apps/backend/app/
  shared/
    __init__.py
    uid.py
    schemas/
      __init__.py
      response.py
  interface/
    http/
      routers/
        _spec.py   # GET /_spec/ok, /_spec/error

apps/backend/tests/
  unit/
    shared/
      test_uid.py
      test_response_schemas.py
  integration/
    test_api_standard_response.py

apps/frontend/src/
  shared/
    lib/
      date.ts
      date.test.ts
    api/
      client.ts
      errors.ts
      errors.test.ts
    types/
      api.ts
```

---

## 4. 참조

- [conventions.md](../../conventions.md) — 시간, ID, API 컨벤션
- [001-signup-design.md](../01-user-auth/001-signup-design.md) — API `success`/`data`/`error` 형식
- [tdd-guide.md](../../tdd-guide.md) — TDD 워크플로우
