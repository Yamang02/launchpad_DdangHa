# 001-signup 구현 설계 문서

> Spec: [001-signup.md](./001-signup.md)
> Epic: [01-user-auth Planning](../epic/01-user-auth/planning.md)
> Branch: `spec/01-user-auth/001-signup`

---

## 1. 구현 체크리스트

### 1.1 Backend 구현

#### Phase 1: 공통 모듈 (Shared)

- [x] `apps/backend/app/shared/__init__.py` 생성
- [x] `apps/backend/app/shared/uid.py` - ULID 기반 UID 생성 (000-foundation)
  - [x] `generate_uid(prefix: str) -> str`
  - [x] `generate_user_uid() -> str` (prefix: "usr_")
- [ ] `apps/backend/app/shared/security.py` - 비밀번호 해싱
  - [ ] `hash_password(password: str) -> str`
  - [ ] `verify_password(plain: str, hashed: str) -> bool`
- [ ] `apps/backend/app/shared/exceptions.py` - 도메인 예외
  - [ ] `DomainError` (base)
  - [ ] `ValidationError`
  - [ ] `DuplicateEmailError`
- [ ] `apps/backend/app/shared/database.py` - DB 연결 설정
  - [ ] `get_db()` async generator
  - [ ] SQLAlchemy async engine 설정

#### Phase 2: User 도메인

- [ ] `apps/backend/app/user/__init__.py` 생성
- [ ] **Domain Layer**
  - [ ] `apps/backend/app/user/domain/__init__.py`
  - [ ] `apps/backend/app/user/domain/entities.py`
    - [ ] `UserStatus` Enum (active, inactive, suspended)
    - [ ] `User` dataclass
  - [ ] `apps/backend/app/user/domain/repository.py`
    - [ ] `UserRepository` Protocol/ABC
      - [ ] `get_by_email(email: str) -> User | None`
      - [ ] `get_by_uid(uid: str) -> User | None`
      - [ ] `create(user: User) -> User`
- [ ] **Infrastructure Layer**
  - [ ] `apps/backend/app/user/infrastructure/__init__.py`
  - [ ] `apps/backend/app/user/infrastructure/models.py`
    - [ ] `UserModel` SQLAlchemy ORM 모델
  - [ ] `apps/backend/app/user/infrastructure/repository.py`
    - [ ] `SQLAlchemyUserRepository` 구현

#### Phase 3: Auth 도메인 (회원가입)

- [ ] `apps/backend/app/auth/__init__.py` 생성
- [ ] **Application Layer**
  - [ ] `apps/backend/app/auth/application/__init__.py`
  - [ ] `apps/backend/app/auth/application/dtos.py`
    - [ ] `SignupRequest` (Pydantic)
      - [ ] `email: EmailStr`
      - [ ] `password: str` (min 8자, 영문+숫자)
      - [ ] `nickname: str` (2-20자)
    - [ ] `SignupResponse`
      - [ ] `uid: str`
      - [ ] `email: str`
      - [ ] `nickname: str`
  - [ ] `apps/backend/app/auth/application/services.py`
    - [ ] `AuthService.signup(request: SignupRequest) -> SignupResponse`
      1. 이메일 중복 검사
      2. 비밀번호 해싱
      3. User 생성 (UID 자동 생성)
      4. DB 저장
      5. Response 반환
- [ ] **Interface Layer**
  - [ ] `apps/backend/app/auth/interface/__init__.py`
  - [ ] `apps/backend/app/auth/interface/http/__init__.py`
  - [ ] `apps/backend/app/auth/interface/http/router.py`
    - [ ] `POST /api/v1/auth/signup` 엔드포인트
    - [ ] 에러 핸들러 (400, 409)

#### Phase 4: Database Migration

- [ ] Alembic 초기화 (미설정 시)
- [ ] `alembic/versions/001_create_users_table.py`
  - [ ] users 테이블 생성
  - [ ] 인덱스 생성 (uid, email, status, created_at)

#### Phase 5: 라우터 등록

- [ ] `apps/backend/main.py` 에 auth router 등록
- [ ] API prefix: `/api/v1`

---

### 1.2 Backend 테스트

#### Unit Tests

- [ ] `apps/backend/tests/unit/__init__.py`
- [x] `apps/backend/tests/unit/shared/__init__.py`
- [x] `apps/backend/tests/unit/shared/test_uid.py` (000-foundation)
  - [x] ULID 형식 검증 테스트
  - [x] prefix 포함 테스트
- [ ] `apps/backend/tests/unit/shared/test_security.py`
  - [ ] 비밀번호 해싱 테스트
  - [ ] 비밀번호 검증 테스트
- [ ] `apps/backend/tests/unit/auth/__init__.py`
- [ ] `apps/backend/tests/unit/auth/test_dtos.py`
  - [ ] SignupRequest 유효성 검증 테스트
    - [ ] 유효한 요청 통과
    - [ ] 잘못된 이메일 형식 거부
    - [ ] 짧은 비밀번호 거부 (8자 미만)
    - [ ] 영문 없는 비밀번호 거부
    - [ ] 숫자 없는 비밀번호 거부
    - [ ] 짧은 닉네임 거부 (2자 미만)
    - [ ] 긴 닉네임 거부 (20자 초과)

#### Integration Tests

- [ ] `apps/backend/tests/integration/__init__.py`
- [ ] `apps/backend/tests/integration/test_auth_signup.py`
  - [ ] `test_signup_success` - 유효한 정보로 회원가입 성공 (201)
  - [ ] `test_signup_duplicate_email` - 중복 이메일 회원가입 실패 (409)
  - [ ] `test_signup_invalid_email_format` - 잘못된 이메일 형식 거부 (400)
  - [ ] `test_signup_short_password` - 8자 미만 비밀번호 거부 (400)
  - [ ] `test_signup_password_without_letter` - 영문 미포함 비밀번호 거부 (400)
  - [ ] `test_signup_password_without_number` - 숫자 미포함 비밀번호 거부 (400)
  - [ ] `test_signup_short_nickname` - 2자 미만 닉네임 거부 (400)
  - [ ] `test_signup_long_nickname` - 20자 초과 닉네임 거부 (400)
  - [ ] `test_signup_response_format` - 응답 형식 검증 (uid, email, nickname)

---

### 1.3 Frontend 구현

#### Phase 1: Shared 모듈

- [ ] `apps/frontend/src/shared/api/client.ts` - Axios 인스턴스
  - [ ] baseURL 설정
  - [ ] 에러 인터셉터
- [ ] `apps/frontend/src/shared/api/authApi.ts`
  - [ ] `signup(data: SignupData): Promise<SignupResponse>`
- [ ] `apps/frontend/src/shared/types/api.ts`
  - [ ] `ApiResponse<T>` 타입
  - [ ] `ApiError` 타입

#### Phase 2: Features - Auth

- [ ] `apps/frontend/src/features/auth/types.ts`
  - [ ] `SignupFormData` interface
  - [ ] `SignupRequest` interface
  - [ ] `SignupResponse` interface
- [ ] `apps/frontend/src/features/auth/ui/SignupForm.tsx`
  - [ ] 이메일 입력 필드
  - [ ] 비밀번호 입력 필드 (마스킹)
  - [ ] 비밀번호 확인 입력 필드
  - [ ] 닉네임 입력 필드
  - [ ] 회원가입 버튼
  - [ ] 로그인 페이지 링크
  - [ ] 실시간 유효성 검사
  - [ ] 에러 메시지 표시
- [ ] `apps/frontend/src/features/auth/lib/validation.ts`
  - [ ] `validateEmail(email: string): string | null`
  - [ ] `validatePassword(password: string): string | null`
  - [ ] `validatePasswordConfirm(password: string, confirm: string): string | null`
  - [ ] `validateNickname(nickname: string): string | null`

#### Phase 3: Pages

- [ ] `apps/frontend/src/pages/signup/SignupPage.tsx`
  - [ ] SignupForm 통합
  - [ ] 회원가입 성공 시 로그인 페이지로 리다이렉트
  - [ ] 로딩 상태 처리
  - [ ] 서버 에러 메시지 표시

#### Phase 4: 라우팅

- [ ] `apps/frontend/src/app/router.tsx` 에 `/signup` 경로 추가

---

### 1.4 Frontend E2E 테스트 (Playwright)

- [ ] `apps/frontend/e2e/auth/signup.spec.ts`
  - [ ] `회원가입 폼이 올바르게 렌더링됨`
  - [ ] `유효한 정보 입력 시 회원가입 성공 후 로그인 페이지로 이동`
  - [ ] `이메일 형식 오류 시 에러 메시지 표시`
  - [ ] `비밀번호 규칙 미충족 시 에러 메시지 표시`
  - [ ] `비밀번호 확인 불일치 시 에러 메시지 표시`
  - [ ] `중복 이메일 시 에러 메시지 표시`
  - [ ] `로그인 링크 클릭 시 로그인 페이지로 이동`

---

## 2. 상세 설계

### 2.1 파일 구조

```
apps/
├── backend/
│   ├── app/
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── uid.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── exceptions.py
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── domain/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── entities.py
│   │   │   │   └── repository.py
│   │   │   └── infrastructure/
│   │   │       ├── __init__.py
│   │   │       ├── models.py
│   │   │       └── repository.py
│   │   └── auth/
│   │       ├── __init__.py
│   │       ├── application/
│   │       │   ├── __init__.py
│   │       │   ├── dtos.py
│   │       │   └── services.py
│   │       └── interface/
│   │           ├── __init__.py
│   │           └── http/
│   │               ├── __init__.py
│   │               └── router.py
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── shared/
│   │   │   │   ├── test_uid.py
│   │   │   │   └── test_security.py
│   │   │   └── auth/
│   │   │       └── test_dtos.py
│   │   └── integration/
│   │       └── test_auth_signup.py
│   └── alembic/
│       └── versions/
│           └── 001_create_users_table.py
│
└── frontend/
    └── src/
        ├── shared/
        │   ├── api/
        │   │   ├── client.ts
        │   │   └── authApi.ts
        │   └── types/
        │       └── api.ts
        ├── features/
        │   └── auth/
        │       ├── types.ts
        │       ├── ui/
        │       │   └── SignupForm.tsx
        │       └── lib/
        │           └── validation.ts
        └── pages/
            └── signup/
                └── SignupPage.tsx
```

---

### 2.2 API 상세 설계

#### POST /api/v1/auth/signup

**Request:**
```http
POST /api/v1/auth/signup HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "nickname": "홍길동"
}
```

**Response (201 Created):**
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

**Response (400 Bad Request - Validation Error):**
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

**Response (409 Conflict - Duplicate Email):**
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

### 2.3 Backend 코드 설계

#### shared/uid.py

```python
"""ULID 기반 Business ID 생성 유틸리티"""

import ulid


def generate_uid(prefix: str) -> str:
    """prefix가 붙은 ULID 생성

    Args:
        prefix: 도메인 식별 접두사 (예: "usr_", "rtk_")

    Returns:
        "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV" 형태의 문자열
    """
    return f"{prefix}{ulid.new().str}"


def generate_user_uid() -> str:
    """User 도메인용 UID 생성"""
    return generate_uid("usr_")
```

#### shared/security.py

```python
"""비밀번호 해싱 유틸리티"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """비밀번호를 bcrypt로 해싱"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """평문 비밀번호와 해시 비교"""
    return pwd_context.verify(plain_password, hashed_password)
```

#### shared/exceptions.py

```python
"""도메인 예외 정의"""


class DomainError(Exception):
    """도메인 로직 기본 예외"""

    def __init__(self, message: str, code: str = "DOMAIN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class ValidationError(DomainError):
    """입력값 검증 실패 예외"""

    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field


class DuplicateEmailError(DomainError):
    """이메일 중복 예외"""

    def __init__(self, email: str):
        super().__init__(f"이미 사용 중인 이메일입니다: {email}", "EMAIL_ALREADY_EXISTS")
        self.email = email
```

#### user/domain/entities.py

```python
"""User 도메인 엔티티"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """User 도메인 엔티티 (Business ID 기준)"""

    uid: str
    email: str
    password_hash: str
    nickname: str
    status: UserStatus = UserStatus.ACTIVE
    profile_image_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None
```

#### auth/application/dtos.py

```python
"""Auth 관련 DTO 정의"""

import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """회원가입 요청 DTO"""

    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    nickname: str = Field(min_length=2, max_length=20)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("비밀번호에 영문자가 포함되어야 합니다.")
        if not re.search(r"\d", v):
            raise ValueError("비밀번호에 숫자가 포함되어야 합니다.")
        return v


class SignupResponse(BaseModel):
    """회원가입 응답 DTO"""

    uid: str
    email: str
    nickname: str
```

#### auth/application/services.py

```python
"""Auth 애플리케이션 서비스"""

from app.shared.uid import generate_user_uid
from app.shared.security import hash_password
from app.shared.exceptions import DuplicateEmailError
from app.user.domain.entities import User, UserStatus
from app.user.domain.repository import UserRepository
from app.auth.application.dtos import SignupRequest, SignupResponse


class AuthService:
    """인증 관련 비즈니스 로직"""

    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository

    async def signup(self, request: SignupRequest) -> SignupResponse:
        """회원가입 처리

        Args:
            request: 회원가입 요청 데이터

        Returns:
            생성된 사용자 정보

        Raises:
            DuplicateEmailError: 이메일이 이미 존재하는 경우
        """
        # 1. 이메일 중복 검사
        existing_user = await self._user_repository.get_by_email(request.email)
        if existing_user:
            raise DuplicateEmailError(request.email)

        # 2. User 엔티티 생성
        user = User(
            uid=generate_user_uid(),
            email=request.email,
            password_hash=hash_password(request.password),
            nickname=request.nickname,
            status=UserStatus.ACTIVE,
        )

        # 3. DB 저장
        created_user = await self._user_repository.create(user)

        # 4. Response 반환
        return SignupResponse(
            uid=created_user.uid,
            email=created_user.email,
            nickname=created_user.nickname,
        )
```

#### auth/interface/http/router.py

```python
"""Auth HTTP 라우터"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError as PydanticValidationError

from app.shared.exceptions import DuplicateEmailError, ValidationError
from app.auth.application.dtos import SignupRequest, SignupResponse
from app.auth.application.services import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def get_auth_service() -> AuthService:
    """AuthService 의존성 주입"""
    # TODO: 실제 구현 시 DI 컨테이너 사용
    pass


@router.post(
    "/signup",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="이메일과 비밀번호로 새 계정을 생성합니다.",
)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """회원가입 엔드포인트"""
    try:
        response = await auth_service.signup(request)
        return {
            "success": True,
            "data": response.model_dump(),
        }
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message,
                },
            },
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "success": False,
                "error": {
                    "code": e.code,
                    "message": e.message,
                    "details": [{"field": e.field, "message": e.message}] if e.field else [],
                },
            },
        )
```

---

### 2.4 Frontend 코드 설계

#### shared/api/client.ts

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';
import { ApiError } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 에러 인터셉터
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error: ApiError }>) => {
    if (error.response?.data?.error) {
      return Promise.reject(error.response.data.error);
    }
    return Promise.reject({
      code: 'UNKNOWN_ERROR',
      message: '알 수 없는 오류가 발생했습니다.',
    });
  }
);
```

#### features/auth/types.ts

```typescript
export interface SignupFormData {
  email: string;
  password: string;
  passwordConfirm: string;
  nickname: string;
}

export interface SignupRequest {
  email: string;
  password: string;
  nickname: string;
}

export interface SignupResponse {
  uid: string;
  email: string;
  nickname: string;
}
```

#### features/auth/lib/validation.ts

```typescript
export const validateEmail = (email: string): string | null => {
  if (!email) {
    return '이메일을 입력해주세요.';
  }
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    return '올바른 이메일 형식이 아닙니다.';
  }
  return null;
};

export const validatePassword = (password: string): string | null => {
  if (!password) {
    return '비밀번호를 입력해주세요.';
  }
  if (password.length < 8) {
    return '비밀번호는 8자 이상이어야 합니다.';
  }
  if (!/[A-Za-z]/.test(password)) {
    return '비밀번호에 영문자가 포함되어야 합니다.';
  }
  if (!/\d/.test(password)) {
    return '비밀번호에 숫자가 포함되어야 합니다.';
  }
  return null;
};

export const validatePasswordConfirm = (
  password: string,
  confirm: string
): string | null => {
  if (!confirm) {
    return '비밀번호 확인을 입력해주세요.';
  }
  if (password !== confirm) {
    return '비밀번호가 일치하지 않습니다.';
  }
  return null;
};

export const validateNickname = (nickname: string): string | null => {
  if (!nickname) {
    return '닉네임을 입력해주세요.';
  }
  if (nickname.length < 2) {
    return '닉네임은 2자 이상이어야 합니다.';
  }
  if (nickname.length > 20) {
    return '닉네임은 20자 이하여야 합니다.';
  }
  return null;
};
```

#### features/auth/ui/SignupForm.tsx

```tsx
import React, { useState, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { SignupFormData } from '../types';
import {
  validateEmail,
  validatePassword,
  validatePasswordConfirm,
  validateNickname,
} from '../lib/validation';
import { signup } from '../../../shared/api/authApi';
import { ApiError } from '../../../shared/types/api';

export const SignupForm: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<SignupFormData>({
    email: '',
    password: '',
    passwordConfirm: '',
    nickname: '',
  });
  const [errors, setErrors] = useState<Partial<SignupFormData>>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = e.target;
      setFormData((prev) => ({ ...prev, [name]: value }));
      setErrors((prev) => ({ ...prev, [name]: undefined }));
      setServerError(null);
    },
    []
  );

  const validateForm = useCallback((): boolean => {
    const newErrors: Partial<SignupFormData> = {};

    const emailError = validateEmail(formData.email);
    if (emailError) newErrors.email = emailError;

    const passwordError = validatePassword(formData.password);
    if (passwordError) newErrors.password = passwordError;

    const confirmError = validatePasswordConfirm(
      formData.password,
      formData.passwordConfirm
    );
    if (confirmError) newErrors.passwordConfirm = confirmError;

    const nicknameError = validateNickname(formData.nickname);
    if (nicknameError) newErrors.nickname = nicknameError;

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validateForm()) return;

      setIsLoading(true);
      setServerError(null);

      try {
        await signup({
          email: formData.email,
          password: formData.password,
          nickname: formData.nickname,
        });
        navigate('/login', {
          state: { message: '회원가입이 완료되었습니다. 로그인해주세요.' }
        });
      } catch (error) {
        const apiError = error as ApiError;
        if (apiError.code === 'EMAIL_ALREADY_EXISTS') {
          setErrors({ email: apiError.message });
        } else {
          setServerError(apiError.message || '회원가입에 실패했습니다.');
        }
      } finally {
        setIsLoading(false);
      }
    },
    [formData, navigate, validateForm]
  );

  return (
    <form onSubmit={handleSubmit}>
      <h2>회원가입</h2>

      {serverError && <div className="error-message">{serverError}</div>}

      <div className="form-group">
        <label htmlFor="email">이메일</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={handleChange}
          disabled={isLoading}
        />
        {errors.email && <span className="field-error">{errors.email}</span>}
      </div>

      <div className="form-group">
        <label htmlFor="password">비밀번호</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={handleChange}
          disabled={isLoading}
        />
        {errors.password && (
          <span className="field-error">{errors.password}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="passwordConfirm">비밀번호 확인</label>
        <input
          type="password"
          id="passwordConfirm"
          name="passwordConfirm"
          value={formData.passwordConfirm}
          onChange={handleChange}
          disabled={isLoading}
        />
        {errors.passwordConfirm && (
          <span className="field-error">{errors.passwordConfirm}</span>
        )}
      </div>

      <div className="form-group">
        <label htmlFor="nickname">닉네임</label>
        <input
          type="text"
          id="nickname"
          name="nickname"
          value={formData.nickname}
          onChange={handleChange}
          disabled={isLoading}
        />
        {errors.nickname && (
          <span className="field-error">{errors.nickname}</span>
        )}
      </div>

      <button type="submit" disabled={isLoading}>
        {isLoading ? '가입 중...' : '회원가입'}
      </button>

      <p>
        이미 계정이 있으신가요? <Link to="/login">로그인</Link>
      </p>
    </form>
  );
};
```

---

### 2.5 Database Migration

```python
"""001_create_users_table

Revision ID: 001
Create Date: 2025-01-19
"""

from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('uid', sa.String(30), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('nickname', sa.String(50), nullable=False),
        sa.Column('profile_image_url', sa.String(500), nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('uid'),
        sa.UniqueConstraint('email'),
        sa.CheckConstraint("status IN ('active', 'inactive', 'suspended')", name='chk_status'),
    )

    op.create_index('idx_users_uid', 'users', ['uid'])
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_status', 'users', ['status'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_users_created_at')
    op.drop_index('idx_users_status')
    op.drop_index('idx_users_email')
    op.drop_index('idx_users_uid')
    op.drop_table('users')
```

---

## 3. 테스트 시나리오 상세

### 3.1 Backend Integration Test 예시

```python
# apps/backend/tests/integration/test_auth_signup.py

import pytest
from httpx import AsyncClient
from fastapi import status


class TestSignup:
    """회원가입 API 통합 테스트"""

    @pytest.fixture
    def valid_signup_data(self):
        return {
            "email": "test@example.com",
            "password": "securePassword123",
            "nickname": "테스트유저",
        }

    async def test_signup_success(
        self, client: AsyncClient, valid_signup_data: dict
    ):
        """유효한 정보로 회원가입 성공"""
        response = await client.post("/api/v1/auth/signup", json=valid_signup_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["success"] is True
        assert "uid" in data["data"]
        assert data["data"]["uid"].startswith("usr_")
        assert data["data"]["email"] == valid_signup_data["email"]
        assert data["data"]["nickname"] == valid_signup_data["nickname"]

    async def test_signup_duplicate_email(
        self, client: AsyncClient, valid_signup_data: dict
    ):
        """중복 이메일로 회원가입 실패 (409)"""
        # 첫 번째 가입
        await client.post("/api/v1/auth/signup", json=valid_signup_data)

        # 같은 이메일로 재가입 시도
        response = await client.post("/api/v1/auth/signup", json=valid_signup_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        data = response.json()
        assert data["detail"]["error"]["code"] == "EMAIL_ALREADY_EXISTS"

    async def test_signup_invalid_email_format(self, client: AsyncClient):
        """잘못된 이메일 형식 거부 (400)"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "invalid-email",
                "password": "securePassword123",
                "nickname": "테스트",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_short_password(self, client: AsyncClient):
        """8자 미만 비밀번호 거부 (400)"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "short1",
                "nickname": "테스트",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_password_without_letter(self, client: AsyncClient):
        """영문 미포함 비밀번호 거부 (400)"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "12345678",
                "nickname": "테스트",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_password_without_number(self, client: AsyncClient):
        """숫자 미포함 비밀번호 거부 (400)"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "passwordonly",
                "nickname": "테스트",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_short_nickname(self, client: AsyncClient):
        """2자 미만 닉네임 거부 (400)"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "securePassword123",
                "nickname": "A",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_signup_long_nickname(self, client: AsyncClient):
        """20자 초과 닉네임 거부 (400)"""
        response = await client.post(
            "/api/v1/auth/signup",
            json={
                "email": "test@example.com",
                "password": "securePassword123",
                "nickname": "A" * 21,
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

### 3.2 Frontend E2E Test 예시

```typescript
// apps/frontend/e2e/auth/signup.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Signup Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/signup');
  });

  test('회원가입 폼이 올바르게 렌더링됨', async ({ page }) => {
    await expect(page.getByRole('heading', { name: '회원가입' })).toBeVisible();
    await expect(page.getByLabel('이메일')).toBeVisible();
    await expect(page.getByLabel('비밀번호', { exact: true })).toBeVisible();
    await expect(page.getByLabel('비밀번호 확인')).toBeVisible();
    await expect(page.getByLabel('닉네임')).toBeVisible();
    await expect(page.getByRole('button', { name: '회원가입' })).toBeVisible();
    await expect(page.getByRole('link', { name: '로그인' })).toBeVisible();
  });

  test('유효한 정보 입력 시 회원가입 성공 후 로그인 페이지로 이동', async ({
    page,
  }) => {
    await page.getByLabel('이메일').fill('newuser@example.com');
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123');
    await page.getByLabel('비밀번호 확인').fill('securePassword123');
    await page.getByLabel('닉네임').fill('새로운유저');
    await page.getByRole('button', { name: '회원가입' }).click();

    await expect(page).toHaveURL('/login');
    await expect(
      page.getByText('회원가입이 완료되었습니다. 로그인해주세요.')
    ).toBeVisible();
  });

  test('이메일 형식 오류 시 에러 메시지 표시', async ({ page }) => {
    await page.getByLabel('이메일').fill('invalid-email');
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123');
    await page.getByRole('button', { name: '회원가입' }).click();

    await expect(
      page.getByText('올바른 이메일 형식이 아닙니다.')
    ).toBeVisible();
  });

  test('비밀번호 규칙 미충족 시 에러 메시지 표시', async ({ page }) => {
    await page.getByLabel('이메일').fill('test@example.com');
    await page.getByLabel('비밀번호', { exact: true }).fill('short');
    await page.getByRole('button', { name: '회원가입' }).click();

    await expect(
      page.getByText('비밀번호는 8자 이상이어야 합니다.')
    ).toBeVisible();
  });

  test('비밀번호 확인 불일치 시 에러 메시지 표시', async ({ page }) => {
    await page.getByLabel('이메일').fill('test@example.com');
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123');
    await page.getByLabel('비밀번호 확인').fill('differentPassword123');
    await page.getByRole('button', { name: '회원가입' }).click();

    await expect(page.getByText('비밀번호가 일치하지 않습니다.')).toBeVisible();
  });

  test('로그인 링크 클릭 시 로그인 페이지로 이동', async ({ page }) => {
    await page.getByRole('link', { name: '로그인' }).click();

    await expect(page).toHaveURL('/login');
  });
});
```

---

## 4. 환경 변수

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/ddangha

# Security
SECRET_KEY=your-secret-key-min-32-bytes-random-string
BCRYPT_ROUNDS=12

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Frontend (.env)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 5. 의존성 추가

### Backend (pyproject.toml)

```toml
[project.dependencies]
# 기존 의존성에 추가
python-ulid = "^2.2.0"
passlib = {extras = ["bcrypt"], version = "^1.7.4"}
pydantic = {extras = ["email"], version = "^2.5.0"}
```

### Frontend (package.json)

```json
{
  "dependencies": {
    "axios": "^1.6.0",
    "react-router-dom": "^6.21.0"
  }
}
```

---

## 6. Acceptance Criteria

- [ ] `POST /api/v1/auth/signup` 엔드포인트 정상 동작
- [ ] 유효한 이메일/비밀번호/닉네임으로 회원가입 성공 (201)
- [ ] 중복 이메일 회원가입 시 409 에러 반환
- [ ] 비밀번호가 bcrypt로 해싱되어 DB에 저장됨
- [ ] UID가 `usr_` prefix + ULID 형식으로 생성됨
- [ ] 모든 Backend 테스트 케이스 통과
- [ ] 모든 Frontend E2E 테스트 케이스 통과
- [ ] Swagger 문서에 API 자동 생성 확인
- [ ] 회원가입 성공 후 로그인 페이지로 리다이렉트

---

## 7. 참조 문서

- [001-signup.md](./001-signup.md) - 원본 스펙
- [Epic Planning](../../epic/01-user-auth/planning.md) - Epic 전체 계획
- [Conventions](../../conventions.md) - 개발 컨벤션
- [Architecture](../../architecture.md) - 아키텍처 개요
