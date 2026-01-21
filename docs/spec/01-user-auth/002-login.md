# Spec 002: 로그인 (Login)

> Epic: 01-user-auth
> Feature ID: FR-02
> Priority: P0
> Branch: `spec/01-user-auth/002-login`
> 설계 문서: [002-login-design.md](./002-login-design.md)

---

## 1. Overview

사용자가 이메일과 비밀번호로 인증하고 JWT 토큰을 발급받는 로그인 기능을 구현합니다.

### 1.1 User Story

```
AS A 가입된 사용자
I WANT TO 이메일과 비밀번호로 로그인하고 싶다
SO THAT 나의 데이터에 접근할 수 있다
```

### 1.2 Epic 목표

이 기능은 **Epic 01: User & Auth Domain**의 핵심 목표를 달성하기 위한 필수 기능입니다:
- 사용자 인증 시스템 구축
- JWT 기반 토큰 인증 제공
- 보안 강화 (Rate Limiting, 에러 메시지 통일)

### 1.3 Scope

**In Scope:**
- 이메일/비밀번호 입력 폼
- 입력값 유효성 검증 (클라이언트 + 서버)
- 비밀번호 검증
- JWT Access Token 및 Refresh Token 발급
- 사용자 상태 확인 (active/inactive/suspended)
- 마지막 로그인 시간 업데이트
- 로그인 성공 후 메인 페이지로 리다이렉트
- 토큰 저장

**Out of Scope:**
- OAuth 소셜 로그인
- 2FA (Two-Factor Authentication)
- "로그인 상태 유지" 옵션
- 세션 관리 대시보드

---

## 2. API Specification

### 2.1 Endpoint

```
POST /api/v1/auth/login
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
  "password": "securePassword123"
}
```

**Validation Rules:**

| Field | Type | Rules |
|-------|------|-------|
| email | string | Required, 이메일 형식, 최대 255자 |
| password | string | Required, 최소 1자 |

### 2.3 Response

**Success (200 OK):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "rtk_01ARZ3NDEKTSV4RRFFQ69G5FAV",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

**Error - Invalid Credentials (401 Unauthorized):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "이메일 또는 비밀번호가 올바르지 않습니다."
  }
}
```

**Error - Inactive Account (403 Forbidden):**
```json
{
  "success": false,
  "error": {
    "code": "ACCOUNT_INACTIVE",
    "message": "비활성화된 계정입니다. 고객센터로 문의해주세요."
  }
}
```

**Error - Suspended Account (403 Forbidden):**
```json
{
  "success": false,
  "error": {
    "code": "ACCOUNT_SUSPENDED",
    "message": "정지된 계정입니다. 고객센터로 문의해주세요."
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

> **보안 고려사항**: 존재하지 않는 이메일과 잘못된 비밀번호를 구분하지 않습니다. 동일한 에러 메시지를 반환하여 사용자 열거 공격을 방지합니다.

---

## 3. Test Cases

### 3.1 Backend Test Cases

- [ ] 유효한 자격증명으로 로그인 성공
- [ ] 잘못된 비밀번호로 로그인 실패 (401)
- [ ] 존재하지 않는 이메일로 로그인 실패 (401)
- [ ] 잘못된 이메일 형식 거부 (400)
- [ ] 비활성화된 계정 로그인 실패 (403)
- [ ] 정지된 계정 로그인 실패 (403)
- [ ] 로그인 성공 시 `last_login_at` 업데이트 확인
- [ ] 로그인 성공 시 유효한 Access Token 및 Refresh Token 반환
- [ ] Rate limiting 동작 확인 (5회/5분, IP + Email 기준)

### 3.2 Frontend Test Cases

- [ ] 로그인 폼이 올바르게 렌더링됨
- [ ] 유효한 자격증명으로 로그인 성공 후 메인 페이지로 이동
- [ ] 잘못된 자격증명 시 에러 메시지 표시
- [ ] 이메일 형식 오류 시 에러 메시지 표시
- [ ] 비활성화된 계정 로그인 시 에러 메시지 표시
- [ ] 정지된 계정 로그인 시 에러 메시지 표시
- [ ] 회원가입 링크 클릭 시 회원가입 페이지로 이동
- [ ] 로그인 성공 시 토큰이 저장됨

---

## 4. Security Considerations

- **비밀번호 검증**: 해싱된 비밀번호와 평문 비밀번호 비교
- **Rate Limiting**: IP + Email 기준 5회/5분 제한 (NFR-04)
- **JWT 토큰**: 
  - Access Token: 15분 만료
  - Refresh Token: 7일 만료, DB에 저장하여 무효화 가능
- **에러 메시지**: 보안상 구체적인 정보 노출 최소화 (이메일 존재 여부 숨김)
- **HTTPS 필수**: 프로덕션 환경에서만 사용

---

## 5. Acceptance Criteria

- [ ] 유효한 이메일/비밀번호로 로그인 가능
- [ ] 잘못된 자격증명 시 명확한 에러 메시지 표시
- [ ] 비활성화/정지된 계정 로그인 시 적절한 에러 메시지 표시
- [ ] 로그인 성공 시 Access Token 및 Refresh Token 발급
- [ ] 로그인 성공 시 `last_login_at` 업데이트
- [ ] Rate limiting 동작 확인
- [ ] 모든 Backend 테스트 케이스 통과
- [ ] 모든 Frontend E2E 테스트 케이스 통과
- [ ] API 문서 (Swagger) 자동 생성 확인

---

## 6. Dependencies

**이 스펙이 의존하는 것:**
- 001-signup (회원가입) - User 도메인 및 DB 스키마

**이 스펙에 의존하는 것:**
- 003-logout (로그아웃)
- 004-refresh (토큰 갱신)
- 005-user-profile (내 정보 조회)

---

## 7. References

- [Epic Planning](../epic/01-user-auth/planning.md)
- [Spec 001: 회원가입](./001-signup.md)
- [설계 문서: 002-login-design.md](./002-login-design.md)
- [Development Guide](../../Development%20Guide.md)
- [Conventions](../conventions.md)
