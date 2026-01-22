# Epic 01: User & Auth Domain

> 사용자 인증 및 계정 관리를 위한 핵심 도메인 구축

## 1. PRD (Product Requirements Document)

### 1.1 개요

| 항목 | 내용 |
|------|------|
| Epic 이름 | User & Auth Domain |
| 목표 | 사용자 회원가입, 로그인, 인증 기능 제공 |
| 우선순위 | P0 (필수) |
| 담당 | 땅콩맛 하쿠 |

### 1.2 배경 및 목적

모든 서비스의 기반이 되는 사용자 인증 시스템을 구축합니다.
빌더톤 환경에 맞게 **최소 기능**으로 시작하되, 확장 가능한 구조를 유지합니다.

### 1.3 핵심 요구사항

#### 기능 요구사항 (Functional Requirements)

| ID | 기능 | 설명 | 우선순위 |
|----|------|------|----------|
| FR-01 | 회원가입 | 이메일/비밀번호로 계정 생성 | P0 |
| FR-02 | 로그인 | 이메일/비밀번호로 인증 | P0 |
| FR-03 | 로그아웃 | 세션/토큰 무효화 | P0 |
| FR-04 | 토큰 갱신 | Access Token 만료 시 Refresh Token으로 갱신 | P0 |
| FR-05 | 내 정보 조회 | 로그인한 사용자 정보 조회 | P1 |
| FR-06 | 내 정보 수정 | 닉네임, 프로필 이미지 등 수정 | P1 |
| FR-07 | 비밀번호 변경 | 현재 비밀번호 확인 후 변경 | P2 |
| FR-08 | 회원 탈퇴 | 계정 비활성화 (soft delete) | P2 |

#### 비기능 요구사항 (Non-Functional Requirements)

| ID | 항목 | 요구사항 |
|----|------|----------|
| NFR-01 | 보안 | 비밀번호 bcrypt 해싱, JWT 토큰 인증 |
| NFR-02 | 성능 | 인증 API 응답 < 500ms |
| NFR-03 | 확장성 | OAuth2 소셜 로그인 확장 가능한 구조 |
| NFR-04 | Rate Limiting | 로그인 실패 5회 시 5분 대기, 회원가입 IP당 분당 3회 |
| NFR-05 | CORS | 허용된 origin만 접근 가능 (환경변수로 관리) |
| NFR-06 | Input Validation | 모든 사용자 입력 서버측 검증 (Pydantic) |

### 1.4 사용자 스토리

```
AS A 신규 사용자
I WANT TO 이메일과 비밀번호로 회원가입하고 싶다
SO THAT 서비스를 이용할 수 있다

AS A 가입된 사용자
I WANT TO 이메일과 비밀번호로 로그인하고 싶다
SO THAT 나의 데이터에 접근할 수 있다

AS A 로그인한 사용자
I WANT TO 내 정보를 확인하고 수정하고 싶다
SO THAT 최신 정보를 유지할 수 있다
```

### 1.5 범위

#### In Scope (이번 에픽에서 구현)
- 이메일/비밀번호 기반 인증
- JWT Access/Refresh Token
- 기본 사용자 CRUD
- 비밀번호 해싱

#### Out of Scope (향후 에픽에서 고려)
- OAuth2 소셜 로그인 (Google, Kakao 등)
- 이메일 인증/비밀번호 찾기
- 2FA (Two-Factor Authentication)
- 세션 관리 대시보드

---

## 2. Domain Schema Design

> **ID/시간 컨벤션**은 [conventions.md](../../conventions.md)를 참조합니다.

### 2.1 ID 전략: ULID 기반 Business ID

프로젝트 전역에서 통일된 ID 생성 전략을 사용합니다.

| 구분 | DB ID | Business ID (uid) |
|------|-------|-------------------|
| 용도 | 내부 참조, FK 관계 | 외부 노출, API 응답 |
| 형식 | `BIGSERIAL` | `ULID` with prefix |
| 노출 | 절대 외부 노출 금지 | URL, 응답에서 사용 |
| 예시 | `id = 1` | `uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"` |

**ULID 선택 이유:**
- **시간순 정렬**: 타임스탬프 48비트로 인덱싱 효율 (B-tree 친화적)
- **분산 환경**: 머신 ID 조정 불필요 (Lambda 환경에 적합)
- **URL-safe**: 26자 Crockford's Base32 인코딩
- **보안**: Sequential ID 노출 방지

**ULID 구조:**
```
 01ARZ3NDEKTSV4RRFFQ69G5FAV
 |----------|------------|
 Timestamp   Randomness
 (48 bits)   (80 bits)
 10자         16자
```

### 2.2 User Entity

업계 표준 사용자 스키마를 기반으로 빌더톤에 필요한 최소 필드로 구성합니다.

```python
# backend/app/user/domain/entities.py

from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class User:
    """User 도메인 엔티티 (Business ID 기준)"""

    uid: str                       # Business ID (ULID, "usr_" prefix)
    email: str                     # 이메일 (unique, 로그인 ID)
    password_hash: str             # 해싱된 비밀번호
    nickname: str                  # 닉네임 (표시 이름)
    profile_image_url: str | None  # 프로필 이미지 URL
    status: UserStatus             # 계정 상태
    created_at: datetime           # 생성 시각 (UTC)
    updated_at: datetime           # 수정 시각 (UTC)
    last_login_at: datetime | None # 마지막 로그인 시각 (UTC)
```

> **Note**: 도메인 엔티티에서는 DB ID(`id`)를 노출하지 않습니다.
> Repository 계층에서 DB 모델 ↔ 도메인 엔티티 변환 시 `uid`만 매핑합니다.

### 2.3 공통 UID 생성 유틸리티

애플리케이션 레벨에서 ULID를 생성합니다 (DB 함수 대신).

```python
# backend/app/shared/uid.py

import ulid

def generate_uid(prefix: str) -> str:
    """prefix가 붙은 ULID 생성

    Args:
        prefix: 도메인 식별 접두사 (예: "usr_", "rtk_")

    Returns:
        "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV" 형태의 문자열
    """
    return f"{prefix}{ulid.new().str}"

# 도메인별 헬퍼 함수
def generate_user_uid() -> str:
    return generate_uid("usr_")

def generate_token_uid() -> str:
    return generate_uid("rtk_")
```

### 2.4 Database Schema

```sql
-- users 테이블
CREATE TABLE users (
    -- DB ID: 내부 전용, FK 관계에 사용
    id BIGSERIAL PRIMARY KEY,

    -- Business ID: ULID 기반 (앱에서 생성, prefix: "usr_")
    -- 길이: prefix(4) + ULID(26) = 30자
    uid VARCHAR(30) NOT NULL UNIQUE,

    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(50) NOT NULL,
    profile_image_url VARCHAR(500),
    status VARCHAR(20) NOT NULL DEFAULT 'active',

    -- 시간: 모두 UTC로 저장
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT chk_status CHECK (status IN ('active', 'inactive', 'suspended'))
);

-- 인덱스: ULID는 시간순 정렬되므로 B-tree 인덱스 효율적
CREATE INDEX idx_users_uid ON users(uid);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at);

-- refresh_tokens 테이블 (토큰 관리)
CREATE TABLE refresh_tokens (
    -- DB ID: 내부 전용
    id BIGSERIAL PRIMARY KEY,

    -- Business ID: ULID 기반 (앱에서 생성, prefix: "rtk_")
    uid VARCHAR(30) NOT NULL UNIQUE,

    -- FK는 DB ID로 참조 (성능)
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    token_hash VARCHAR(255) NOT NULL UNIQUE,

    -- 시간: 모두 UTC로 저장
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    revoked_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_refresh_tokens_uid ON refresh_tokens(uid);
CREATE INDEX idx_refresh_tokens_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires_at ON refresh_tokens(expires_at);
```

### 2.5 ID 사용 가이드라인

> 상세 가이드라인은 [conventions.md](../../conventions.md#id-생성-전략)를 참조합니다.

```python
# API 응답 예시 - uid만 노출
{
    "data": {
        "uid": "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV",  # Business ID (ULID)
        "email": "user@example.com",
        "nickname": "홍길동",
        "created_at": "2025-01-19T15:30:00Z"      # UTC ISO 8601
        # id는 절대 포함하지 않음!
    }
}
```

### 2.6 API Endpoints

| Method | Endpoint | 설명 | Auth |
|--------|----------|------|------|
| POST | `/api/v1/auth/signup` | 회원가입 | - |
| POST | `/api/v1/auth/login` | 로그인 | - |
| POST | `/api/v1/auth/logout` | 로그아웃 | Required |
| POST | `/api/v1/auth/refresh` | 토큰 갱신 | Refresh Token |
| GET | `/api/v1/users/me` | 내 정보 조회 | Required |
| PATCH | `/api/v1/users/me` | 내 정보 수정 | Required |
| PATCH | `/api/v1/users/me/password` | 비밀번호 변경 | Required |
| DELETE | `/api/v1/users/me` | 회원 탈퇴 | Required |

### 2.7 Request/Response DTOs

```python
# 회원가입
class SignupRequest:
    email: str          # 이메일 형식 검증
    password: str       # 최소 8자, 영문+숫자
    nickname: str       # 2-20자

class SignupResponse:
    uid: str            # Business ID (예: "usr_a1b2c3...")
    email: str
    nickname: str

# 로그인
class LoginRequest:
    email: str
    password: str

class LoginResponse:
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # 초 단위

# 사용자 정보
class UserResponse:
    uid: str            # Business ID (예: "usr_a1b2c3...")
    email: str
    nickname: str
    profile_image_url: str | None
    status: str
    created_at: datetime

class UpdateUserRequest:
    nickname: str | None
    profile_image_url: str | None
```

---

## 3. Architecture & Directory Structure

프로젝트 아키텍처 문서에 따른 경량 헥사고널 구조를 적용합니다.

### 3.1 Backend Structure

**레이어별 구조 (Layer-based):**

```
backend/app/
├── domain/                        # 도메인 레이어
│   ├── user/
│   │   ├── __init__.py
│   │   ├── entities.py            # User 엔티티
│   │   ├── value_objects.py       # Email, Password 등 VO
│   │   └── repository.py          # Repository 인터페이스
│   └── auth/
│       ├── __init__.py
│       ├── entities.py            # RefreshToken 엔티티
│       └── repository.py          # Repository 인터페이스
│
├── application/                   # 애플리케이션 레이어
│   ├── user/
│   │   ├── __init__.py
│   │   ├── services.py            # UserService
│   │   └── dtos.py                # Request/Response DTO
│   └── auth/
│       ├── __init__.py
│       ├── services.py            # AuthService
│       └── dtos.py                # Request/Response DTO
│
├── infrastructure/                # 인프라스트럭처 레이어
│   ├── user/
│   │   ├── __init__.py
│   │   ├── models.py              # SQLAlchemy ORM 모델
│   │   └── repository.py          # SQLAlchemy Repository 구현
│   └── auth/
│       ├── __init__.py
│       ├── jwt_handler.py         # JWT 토큰 처리
│       └── repository.py          # Token Repository 구현
│
├── interface/                     # 인터페이스 레이어
│   └── http/
│       ├── __init__.py
│       ├── routers/
│       │   ├── __init__.py
│       │   ├── user.py            # /users 라우터
│       │   └── auth.py            # /auth 라우터
│       └── dependencies.py        # FastAPI Depends (인증)
│
└── shared/                        # 공통 모듈
    ├── __init__.py
    ├── uid.py                     # ULID 기반 Business ID 생성
    ├── database.py                # DB 연결 설정
    ├── security.py                # 비밀번호 해싱
    ├── exceptions.py              # 공통 예외
    └── rate_limiter.py            # Rate Limiting 유틸리티
```

**구조 선택 이유:**
- 레이어별 의존성 관리가 명확함
- 아키텍처 문서와 일치
- 같은 레이어의 코드를 한 곳에서 찾을 수 있음

### 3.2 Frontend Structure (FSD)

```
frontend/src/
├── shared/
│   ├── api/
│   │   └── authApi.ts            # 인증 API 클라이언트
│   ├── lib/
│   │   └── tokenStorage.ts       # 토큰 저장소
│   └── ui/
│       └── Input/                # 공통 Input 컴포넌트
│
├── entities/
│   └── user/
│       ├── model/
│       │   └── types.ts          # User 타입 정의
│       └── api/
│           └── userApi.ts        # User API
│
├── features/
│   ├── auth/
│   │   ├── ui/
│   │   │   ├── LoginForm.tsx
│   │   │   └── SignupForm.tsx
│   │   ├── model/
│   │   │   └── useAuth.ts        # 인증 상태 훅
│   │   └── api/
│   │       └── authApi.ts
│   │
│   └── user/
│       └── ui/
│           ├── ProfileEdit.tsx
│           └── PasswordChange.tsx
│
└── pages/
    ├── login/
    │   └── LoginPage.tsx
    ├── signup/
    │   └── SignupPage.tsx
    └── profile/
        └── ProfilePage.tsx
```

---

## 4. TDD Strategy

### 4.1 Backend 테스트 계획 (pytest)

```python
# 테스트 파일 구조
backend/tests/
├── unit/
│   ├── user/
│   │   ├── test_user_entity.py      # 엔티티 로직 테스트
│   │   └── test_user_service.py     # 서비스 로직 테스트
│   └── auth/
│       ├── test_jwt_handler.py      # JWT 생성/검증 테스트
│       └── test_auth_service.py     # 인증 서비스 테스트
│
├── integration/
│   ├── test_auth_api.py             # 인증 API 통합 테스트
│   └── test_user_api.py             # 사용자 API 통합 테스트
│
└── conftest.py                      # pytest fixtures
```

#### 핵심 테스트 케이스

**Auth Domain:**
```
- [x] 유효한 정보로 회원가입 성공
- [x] 중복 이메일로 회원가입 실패
- [x] 유효하지 않은 이메일 형식 거부
- [x] 짧은 비밀번호 거부 (8자 미만)
- [x] 올바른 자격증명으로 로그인 성공
- [x] 잘못된 비밀번호로 로그인 실패
- [x] 존재하지 않는 이메일로 로그인 실패
- [x] 유효한 refresh token으로 토큰 갱신 성공
- [x] 만료된 refresh token으로 토큰 갱신 실패
- [x] 로그아웃 시 refresh token 무효화
```

**User Domain:**
```
- [x] 인증된 사용자 본인 정보 조회 성공
- [x] 인증 없이 정보 조회 실패 (401)
- [x] 닉네임 수정 성공
- [x] 프로필 이미지 URL 수정 성공
- [x] 올바른 현재 비밀번호로 비밀번호 변경 성공
- [x] 잘못된 현재 비밀번호로 비밀번호 변경 실패
- [x] 회원 탈퇴 시 status가 inactive로 변경
```

### 4.2 Frontend 테스트 계획 (Playwright)

```typescript
// 테스트 파일 구조
frontend/e2e/
├── auth/
│   ├── signup.spec.ts
│   ├── login.spec.ts
│   └── logout.spec.ts
│
├── user/
│   ├── profile-view.spec.ts
│   └── profile-edit.spec.ts
│
└── fixtures/
    └── auth.ts                    # 인증 관련 fixtures
```

#### 핵심 테스트 시나리오

**회원가입:**
```
- [x] 회원가입 폼이 올바르게 렌더링됨
- [x] 유효한 정보 입력 시 회원가입 성공 후 로그인 페이지로 이동
- [x] 이메일 형식 오류 시 에러 메시지 표시
- [x] 비밀번호 규칙 미충족 시 에러 메시지 표시
- [x] 중복 이메일 시 에러 메시지 표시
```

**로그인:**
```
- [x] 로그인 폼이 올바르게 렌더링됨
- [x] 유효한 자격증명으로 로그인 성공 후 메인 페이지로 이동
- [x] 잘못된 자격증명 시 에러 메시지 표시
- [x] 회원가입 링크 클릭 시 회원가입 페이지로 이동
```

**프로필:**
```
- [x] 로그인 후 프로필 페이지 접근 가능
- [x] 사용자 정보가 올바르게 표시됨
- [x] 닉네임 수정 후 성공 메시지 표시
- [x] 비밀번호 변경 성공 후 확인 메시지 표시
```

---

## 5. Implementation Plan

### Phase 1: 기반 설정

1. **DB 마이그레이션 설정**
   - Alembic 초기화
   - users, refresh_tokens 테이블 생성 마이그레이션

2. **공통 모듈 구현**
   - `shared/database.py`: DB 연결 설정
   - `shared/security.py`: bcrypt 해싱 유틸리티
   - `shared/exceptions.py`: 도메인 예외 클래스

### Phase 2: User Domain

1. **Domain Layer**
   - User 엔티티 정의
   - UserRepository 인터페이스 정의

2. **Infrastructure Layer**
   - SQLAlchemy User 모델
   - UserRepository 구현

3. **Application Layer**
   - UserService 구현 (CRUD)
   - DTOs 정의

4. **Interface Layer**
   - `/api/v1/users` 라우터

5. **Tests**
   - Unit tests (entity, service)
   - Integration tests (API)

### Phase 3: Auth Domain

1. **Domain Layer**
   - RefreshToken 엔티티
   - TokenRepository 인터페이스

2. **Infrastructure Layer**
   - JWT Handler (생성, 검증, 갱신)
   - TokenRepository 구현

3. **Application Layer**
   - AuthService (signup, login, logout, refresh)
   - DTOs 정의

4. **Interface Layer**
   - `/api/v1/auth` 라우터
   - 인증 미들웨어/의존성

5. **Tests**
   - Unit tests (jwt, service)
   - Integration tests (API)

### Phase 4: Frontend

1. **Shared & Entities**
   - API 클라이언트 설정
   - User 타입 정의
   - Token 저장소

2. **Features**
   - LoginForm, SignupForm 컴포넌트
   - useAuth 훅
   - ProfileEdit 컴포넌트

3. **Pages**
   - LoginPage, SignupPage, ProfilePage

4. **E2E Tests (Playwright)**
   - 회원가입, 로그인, 프로필 테스트

---

## 6. Dependencies

### Backend

```toml
# pyproject.toml 추가 의존성
[project.dependencies]
python-ulid = "^2.2.0"     # ULID 생성 (시간순 정렬 가능 ID)
pyjwt = "^2.8.0"           # JWT 토큰 처리
passlib = "^1.7.4"         # 비밀번호 해싱
bcrypt = "^4.1.0"          # bcrypt 알고리즘
python-multipart = "^0.0.6" # Form 데이터 처리
```

### Frontend

```json
// package.json 추가 의존성
{
  "dependencies": {
    "axios": "^1.6.0",
    "zustand": "^4.4.0"
  }
}
```

---

## 7. Security Configuration

### 7.1 JWT 토큰 설정

| 항목 | 값 | 비고 |
|------|-----|------|
| Access Token 만료 | 15분 | 짧게 유지하여 탈취 시 피해 최소화 |
| Refresh Token 만료 | 7일 | 재로그인 주기 |
| 알고리즘 | HS256 | HMAC SHA-256 |
| Secret Key | 환경변수 | 최소 32바이트 랜덤 문자열 |

```python
# backend/app/auth/infrastructure/jwt_handler.py

JWT_CONFIG = {
    "access_token_expire_minutes": 15,
    "refresh_token_expire_days": 7,
    "algorithm": "HS256",
}
```

### 7.2 Refresh Token Rotation

보안 강화를 위해 Refresh Token 사용 시 새 토큰을 발급합니다:

```
1. Client → /auth/refresh (old_refresh_token)
2. Server: old_refresh_token 검증 및 무효화
3. Server: 새 access_token + 새 refresh_token 발급
4. Client: 새 토큰 저장, 이전 토큰 폐기
```

**장점:**
- 탈취된 토큰의 유효 기간 최소화
- 동시 세션 탐지 가능 (이미 사용된 토큰 재사용 시)

### 7.3 Rate Limiting 정책

| 엔드포인트 | 제한 | 기준 |
|-----------|------|------|
| POST /auth/login | 5회/5분 | IP + Email |
| POST /auth/signup | 3회/분 | IP |
| POST /auth/refresh | 10회/분 | User |
| 기타 인증 필요 API | 100회/분 | User |

### 7.4 CORS 설정

```python
# backend/app/main.py

CORS_CONFIG = {
    "allow_origins": os.getenv("CORS_ORIGINS", "").split(","),
    "allow_credentials": True,
    "allow_methods": ["GET", "POST", "PATCH", "DELETE"],
    "allow_headers": ["Authorization", "Content-Type"],
}
```

---

## 8. Risks & Mitigations

| 리스크 | 영향 | 완화 방안 |
|--------|------|-----------|
| JWT 보안 취약점 | High | 짧은 access token 만료 (15분), refresh token rotation |
| 비밀번호 유출 | High | bcrypt 해싱, 평문 로깅 금지 |
| Token 탈취 | Medium | HTTPS 필수, HttpOnly 쿠키 고려 |
| 브루트포스 공격 | Medium | Rate limiting (NFR-04) |
| 대량 가입 시도 | Low | Rate limiting (NFR-04) |

---

## 9. Acceptance Criteria

이 에픽이 완료되었다고 판단하는 기준:

- [ ] 모든 P0 기능 구현 완료
- [ ] Backend 테스트 커버리지 80% 이상
- [ ] Frontend E2E 테스트 모든 시나리오 통과
- [ ] API 문서 (Swagger) 자동 생성 확인
- [ ] 코드 리뷰 완료 및 main 브랜치 머지

---

## 10. References

- [프로젝트 아키텍처](../../architecture.md)
- [개발 컨벤션](../../conventions.md)
- [TDD 가이드](../../tdd-guide.md)
- [기술 스택](../../tech-stack.md)
