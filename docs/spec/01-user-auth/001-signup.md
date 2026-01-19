# Spec 001: 회원가입 (Signup)

> Epic: 01-user-auth
> Feature ID: FR-01
> Priority: P0
> Branch: `spec/01-user-auth/001-signup`

---

## 1. Overview

사용자가 이메일과 비밀번호로 새 계정을 생성할 수 있는 회원가입 기능을 구현합니다.

### 1.1 User Story

```
AS A 신규 사용자
I WANT TO 이메일과 비밀번호로 회원가입하고 싶다
SO THAT 서비스를 이용할 수 있다
```

### 1.2 Scope

**In Scope:**
- 이메일/비밀번호/닉네임 입력 폼
- 입력값 유효성 검증 (클라이언트 + 서버)
- 비밀번호 해싱 및 저장
- 중복 이메일 검사
- 회원가입 성공 후 로그인 페이지로 리다이렉트

**Out of Scope:**
- 이메일 인증
- OAuth 소셜 로그인
- 약관 동의 (추후 스펙에서 추가)

---

## 2. API Specification

### 2.1 Endpoint

```
POST /api/v1/auth/signup
```

### 2.2 Request

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "nickname": "홍길동"
}
```

**Validation Rules:**

| Field | Type | Rules |
|-------|------|-------|
| email | string | Required, 이메일 형식, 최대 255자 |
| password | string | Required, 최소 8자, 영문+숫자 포함 |
| nickname | string | Required, 2-20자 |

### 2.3 Response

**Success (201 Created):**
```json
{
  "success": true,
  "data": {
    "uid": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "email": "user@example.com",
    "nickname": "홍길동"
  }
}
```

**Error - Validation (400 Bad Request):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다.",
    "details": [
      {
        "field": "email",
        "message": "올바른 이메일 형식이 아닙니다."
      }
    ]
  }
}
```

**Error - Duplicate Email (409 Conflict):**
```json
{
  "success": false,
  "error": {
    "code": "EMAIL_ALREADY_EXISTS",
    "message": "이미 사용 중인 이메일입니다."
  }
}
```

---

## 3. Database Changes

### 3.1 Migration

`users` 테이블은 Epic planning에서 정의된 스키마를 사용합니다.

```sql
-- Migration: 001_create_users_table.sql

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    uid VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    profile_image_url VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_users_uid ON users(uid);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);
```

---

## 4. Backend Implementation

### 4.1 Directory Structure

```
backend/app/
├── auth/
│   ├── application/
│   │   ├── dtos.py          # SignupRequest, SignupResponse
│   │   └── services.py      # AuthService.signup()
│   └── interface/
│       └── http/
│           └── router.py    # POST /auth/signup
├── user/
│   ├── domain/
│   │   ├── entities.py      # User entity
│   │   └── repository.py    # UserRepository interface
│   └── infrastructure/
│       └── repository.py    # SQLAlchemy implementation
└── shared/
    ├── uid.py               # generate_user_uid()
    └── security.py          # hash_password()
```

### 4.2 Key Components

**DTOs (auth/application/dtos.py):**
```python
from pydantic import BaseModel, EmailStr, Field

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, pattern=r'^(?=.*[A-Za-z])(?=.*\d).+$')
    nickname: str = Field(min_length=2, max_length=20)

class SignupResponse(BaseModel):
    uid: str
    email: str
    nickname: str
```

**Service (auth/application/services.py):**
```python
class AuthService:
    async def signup(self, request: SignupRequest) -> SignupResponse:
        # 1. 이메일 중복 검사
        # 2. 비밀번호 해싱
        # 3. User 생성 (UID 자동 생성)
        # 4. DB 저장
        # 5. Response 반환
        pass
```

---

## 5. Frontend Implementation

### 5.1 Directory Structure

```
frontend/src/
├── features/
│   └── auth/
│       ├── ui/
│       │   └── SignupForm.tsx
│       └── api/
│           └── authApi.ts
└── pages/
    └── signup/
        └── SignupPage.tsx
```

### 5.2 UI Components

**SignupForm:**
- 이메일 입력 필드
- 비밀번호 입력 필드 (마스킹)
- 비밀번호 확인 입력 필드
- 닉네임 입력 필드
- 회원가입 버튼
- 로그인 페이지 링크

**Validation (Client-side):**
- 실시간 입력값 검증
- 에러 메시지 표시
- 비밀번호 확인 일치 검사

---

## 6. Test Cases

### 6.1 Backend Tests (pytest)

```python
# tests/integration/test_auth_signup.py

class TestSignup:
    async def test_signup_success(self):
        """유효한 정보로 회원가입 성공"""

    async def test_signup_duplicate_email(self):
        """중복 이메일로 회원가입 실패 (409)"""

    async def test_signup_invalid_email_format(self):
        """잘못된 이메일 형식 거부 (400)"""

    async def test_signup_short_password(self):
        """8자 미만 비밀번호 거부 (400)"""

    async def test_signup_password_without_letter(self):
        """영문 미포함 비밀번호 거부 (400)"""

    async def test_signup_password_without_number(self):
        """숫자 미포함 비밀번호 거부 (400)"""

    async def test_signup_short_nickname(self):
        """2자 미만 닉네임 거부 (400)"""

    async def test_signup_long_nickname(self):
        """20자 초과 닉네임 거부 (400)"""
```

### 6.2 Frontend Tests (Playwright)

```typescript
// e2e/auth/signup.spec.ts

describe('Signup Page', () => {
  test('회원가입 폼이 올바르게 렌더링됨');
  test('유효한 정보 입력 시 회원가입 성공 후 로그인 페이지로 이동');
  test('이메일 형식 오류 시 에러 메시지 표시');
  test('비밀번호 규칙 미충족 시 에러 메시지 표시');
  test('비밀번호 확인 불일치 시 에러 메시지 표시');
  test('중복 이메일 시 에러 메시지 표시');
  test('로그인 링크 클릭 시 로그인 페이지로 이동');
});
```

---

## 7. Security Considerations

- **비밀번호 해싱**: bcrypt 사용 (cost factor: 12)
- **Rate Limiting**: IP당 분당 3회 제한 (NFR-04)
- **Input Sanitization**: Pydantic 검증으로 SQL Injection 방지
- **Error Messages**: 보안상 구체적인 정보 노출 최소화

---

## 8. Acceptance Criteria

- [ ] 유효한 이메일/비밀번호/닉네임으로 회원가입 가능
- [ ] 중복 이메일 회원가입 시 명확한 에러 메시지 표시
- [ ] 비밀번호는 bcrypt로 해싱되어 저장됨
- [ ] 모든 Backend 테스트 케이스 통과
- [ ] 모든 Frontend E2E 테스트 케이스 통과
- [ ] API 문서 (Swagger) 자동 생성 확인

---

## 9. Dependencies

**이 스펙이 의존하는 것:**
- 없음 (첫 번째 스펙)

**이 스펙에 의존하는 것:**
- 002-login (로그인)
- 005-user-profile (내 정보 조회)

---

## 10. References

- [Epic Planning](../epic/01-user-auth/planning.md)
- [Development Guide](../../Development%20Guide.md)
- [Conventions](../conventions.md)
