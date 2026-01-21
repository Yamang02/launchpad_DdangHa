# 002-login 구현 설계 문서

> Spec: [002-login.md](./002-login.md)
> Epic: [01-user-auth Planning](../epic/01-user-auth/planning.md)
> Branch: `spec/01-user-auth/002-login`

---

## 1. 구현 체크리스트

### 1.1 Backend 구현

#### Phase 1: JWT Handler (Infrastructure)

- [ ] `apps/backend/app/auth/infrastructure/__init__.py` 생성
- [ ] `apps/backend/app/auth/infrastructure/jwt_handler.py`
  - [ ] `create_access_token(data: Dict[str, str]) -> str`
    - [ ] JWT Secret Key 환경변수에서 로드
    - [ ] Access Token 만료 시간: 15분
    - [ ] 알고리즘: HS256
    - [ ] Payload: `{"sub": user_uid, "exp": expire, "type": "access"}`
  - [ ] `create_refresh_token(uid: str) -> str`
    - [ ] Refresh Token 만료 시간: 7일
    - [ ] Payload: `{"uid": uid, "exp": expire, "type": "refresh"}`
  - [ ] `verify_token(token: str) -> Dict[str, Any] | None`
    - [ ] 토큰 검증 및 디코딩
    - [ ] 만료 시간 확인
    - [ ] 타입 확인 (access/refresh)
  - [ ] `get_token_uid(payload: Dict[str, Any]) -> str | None`
    - [ ] Payload에서 uid 추출

#### Phase 2: Auth Service (Application)

- [ ] `apps/backend/app/auth/application/dtos.py` 업데이트
  - [ ] `LoginRequest` (Pydantic)
    - [ ] `email: EmailStr`
    - [ ] `password: str`
  - [ ] `LoginResponse` (Pydantic)
    - [ ] `access_token: str`
    - [ ] `refresh_token: str`
    - [ ] `token_type: str = "Bearer"`
    - [ ] `expires_in: int` (초 단위, 900 = 15분)
- [ ] `apps/backend/app/auth/application/services.py` 업데이트
  - [ ] `AuthService.login(request: LoginRequest) -> LoginResponse`
    1. 이메일로 사용자 조회 (`get_by_email`)
    2. 사용자 존재 여부 확인 → 없으면 `InvalidCredentialsError`
    3. 계정 상태 확인:
       - `INACTIVE` → `InactiveAccountError`
       - `SUSPENDED` → `SuspendedAccountError`
    4. 비밀번호 검증 (`verify_password`)
    5. 비밀번호 불일치 → `InvalidCredentialsError`
    6. `last_login_at` 업데이트 (`update_last_login`)
    7. Access Token 생성 (`create_access_token`)
    8. Refresh Token 생성 (`create_refresh_token`)
    9. Refresh Token DB 저장 (추후 구현, 이번 단계에서는 스킵)
    10. `LoginResponse` 반환

#### Phase 3: User Repository 확장

- [ ] `apps/backend/app/user/domain/repository.py` 업데이트
  - [ ] `UserRepository` Protocol에 메소드 추가:
    - [ ] `update_last_login(uid: str) -> None`
- [ ] `apps/backend/app/user/infrastructure/repository.py` 업데이트
  - [ ] `SQLAlchemyUserRepository.update_last_login()` 구현
    - [ ] `last_login_at`을 현재 시간(UTC)으로 업데이트

#### Phase 4: Exceptions 확장

- [ ] `apps/backend/app/shared/exceptions.py` 업데이트
  - [ ] `InvalidCredentialsError` (DomainError 상속)
    - [ ] `code = "INVALID_CREDENTIALS"`
    - [ ] `message = "이메일 또는 비밀번호가 올바르지 않습니다."`
  - [ ] `InactiveAccountError` (DomainError 상속)
    - [ ] `code = "ACCOUNT_INACTIVE"`
    - [ ] `message = "비활성화된 계정입니다. 고객센터로 문의해주세요."`
  - [ ] `SuspendedAccountError` (DomainError 상속)
    - [ ] `code = "ACCOUNT_SUSPENDED"`
    - [ ] `message = "정지된 계정입니다. 고객센터로 문의해주세요."`

#### Phase 5: HTTP Router

- [ ] `apps/backend/app/auth/interface/http/router.py` 업데이트
  - [ ] `POST /api/v1/auth/login` 엔드포인트
    - [ ] `LoginRequest` 받기
    - [ ] `AuthService.login()` 호출
    - [ ] 성공 시 200 OK, `LoginResponse` 반환
    - [ ] 에러 핸들러:
      - [ ] `InvalidCredentialsError` → 401 Unauthorized
      - [ ] `InactiveAccountError` → 403 Forbidden
      - [ ] `SuspendedAccountError` → 403 Forbidden
      - [ ] `ValidationError` → 400 Bad Request

#### Phase 6: 환경 변수 설정

- [ ] `apps/backend/env.example` 업데이트
  - [ ] `JWT_SECRET_KEY` 추가 (최소 32바이트 랜덤 문자열)
  - [ ] 주석: "JWT 토큰 서명에 사용되는 비밀키 (최소 32바이트)"

---

### 1.2 Backend 테스트

#### Unit Tests

- [ ] `apps/backend/tests/unit/auth/test_jwt_handler.py`
  - [ ] `test_create_access_token` - Access Token 생성 및 검증
  - [ ] `test_create_refresh_token` - Refresh Token 생성 및 검증
  - [ ] `test_verify_token_valid` - 유효한 토큰 검증 성공
  - [ ] `test_verify_token_expired` - 만료된 토큰 검증 실패
  - [ ] `test_verify_token_invalid` - 잘못된 토큰 검증 실패
  - [ ] `test_get_token_uid` - Payload에서 uid 추출
- [ ] `apps/backend/tests/unit/auth/test_dtos.py` 업데이트
  - [ ] `LoginRequest` 유효성 검증 테스트
    - [ ] 유효한 요청 통과
    - [ ] 잘못된 이메일 형식 거부
    - [ ] 빈 비밀번호 거부
- [ ] `apps/backend/tests/unit/user/test_repository_protocol.py` 업데이트
  - [ ] `update_last_login` 메소드 시그니처 확인
- [ ] `apps/backend/tests/unit/user/test_sqlalchemy_user_repository.py` 업데이트
  - [ ] `test_update_last_login` - `last_login_at` 업데이트 확인
- [ ] `apps/backend/tests/unit/shared/test_exceptions.py` 업데이트
  - [ ] `InvalidCredentialsError` 테스트
  - [ ] `InactiveAccountError` 테스트
  - [ ] `SuspendedAccountError` 테스트

#### Integration Tests

- [ ] `apps/backend/tests/integration/test_auth_login.py`
  - [ ] `test_login_success` - 유효한 자격증명으로 로그인 성공 (200)
  - [ ] `test_login_invalid_password` - 잘못된 비밀번호로 로그인 실패 (401)
  - [ ] `test_login_nonexistent_email` - 존재하지 않는 이메일로 로그인 실패 (401)
  - [ ] `test_login_invalid_email_format` - 잘못된 이메일 형식 거부 (422)
  - [ ] `test_login_inactive_account` - 비활성화된 계정 로그인 실패 (403)
  - [ ] `test_login_suspended_account` - 정지된 계정 로그인 실패 (403)
  - [ ] `test_login_updates_last_login_at` - 로그인 성공 시 `last_login_at` 업데이트 확인
  - [ ] `test_login_returns_valid_tokens` - 로그인 성공 시 유효한 Access Token 및 Refresh Token 반환
  - [ ] `test_login_response_format` - 응답 형식 검증 (access_token, refresh_token, token_type, expires_in)

---

### 1.3 Frontend 구현

#### Phase 1: API 클라이언트

- [ ] `apps/frontend/src/shared/api/authApi.ts` 업데이트
  - [ ] `login(data: LoginRequest): Promise<LoginResponse>`
    - [ ] `POST /api/v1/auth/login` 호출
    - [ ] 에러 처리 (401, 403, 400)

#### Phase 2: Token Storage

- [ ] `apps/frontend/src/shared/lib/tokenStorage.ts` 생성
  - [ ] `setAccessToken(token: string): void`
    - [ ] 로컬 스토리지 또는 메모리에 저장
  - [ ] `getAccessToken(): string | null`
  - [ ] `setRefreshToken(token: string): void`
  - [ ] `getRefreshToken(): string | null`
  - [ ] `clearTokens(): void`
    - [ ] 로그아웃 시 토큰 삭제

#### Phase 3: Features - Auth

- [ ] `apps/frontend/src/features/auth/types.ts` 업데이트
  - [ ] `LoginFormData` interface
    - [ ] `email: string`
    - [ ] `password: string`
- [ ] `apps/frontend/src/features/auth/lib/validation.ts` 업데이트
  - [ ] `validateLoginForm(data: LoginFormData): Partial<LoginFormData>`
    - [ ] 이메일 형식 검증
    - [ ] 비밀번호 필수 검증
- [ ] `apps/frontend/src/features/auth/ui/LoginForm.tsx` 생성
  - [ ] 이메일 입력 필드
  - [ ] 비밀번호 입력 필드 (마스킹)
  - [ ] 로그인 버튼
  - [ ] 회원가입 페이지 링크
  - [ ] 실시간 유효성 검사
  - [ ] 에러 메시지 표시
  - [ ] 로딩 상태 표시
  - [ ] 로그인 성공 시:
    - [ ] 토큰 저장 (`setAccessToken`, `setRefreshToken`)
    - [ ] 메인 페이지로 리다이렉트

#### Phase 4: Pages

- [ ] `apps/frontend/src/pages/login/LoginPage.tsx` 생성
  - [ ] LoginForm 통합
  - [ ] 로그인 성공 시 메인 페이지로 리다이렉트
  - [ ] 로딩 상태 처리
  - [ ] 서버 에러 메시지 표시

#### Phase 5: 라우팅

- [ ] `apps/frontend/src/app/App.tsx` 업데이트
  - [ ] `/login` 경로 추가

---

### 1.4 Frontend E2E 테스트 (Playwright)

- [ ] `apps/frontend/e2e/auth/login.spec.ts` 생성
  - [ ] `로그인 폼이 올바르게 렌더링됨`
  - [ ] `유효한 자격증명으로 로그인 성공 후 메인 페이지로 이동`
  - [ ] `잘못된 자격증명 시 에러 메시지 표시`
  - [ ] `이메일 형식 오류 시 에러 메시지 표시`
  - [ ] `비활성화된 계정 로그인 시 에러 메시지 표시`
  - [ ] `정지된 계정 로그인 시 에러 메시지 표시`
  - [ ] `회원가입 링크 클릭 시 회원가입 페이지로 이동`
  - [ ] `로그인 성공 시 토큰이 저장됨`

---

## 2. 상세 설계

### 2.1 파일 구조

```
apps/
├── backend/
│   ├── app/
│   │   ├── auth/
│   │   │   ├── application/
│   │   │   │   ├── dtos.py          # LoginRequest, LoginResponse
│   │   │   │   └── services.py      # AuthService.login()
│   │   │   ├── infrastructure/
│   │   │   │   └── jwt_handler.py   # JWT 토큰 생성/검증
│   │   │   └── interface/
│   │   │       └── http/
│   │   │           └── router.py    # POST /auth/login
│   │   ├── user/
│   │   │   ├── domain/
│   │   │   │   └── repository.py    # UserRepository.update_last_login()
│   │   │   └── infrastructure/
│   │   │       └── repository.py  # SQLAlchemyUserRepository.update_last_login()
│   │   └── shared/
│   │       ├── exceptions.py        # InvalidCredentialsError, InactiveAccountError, SuspendedAccountError
│   │       └── security.py          # verify_password() (이미 구현됨)
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── auth/
│   │   │   │   ├── test_jwt_handler.py
│   │   │   │   └── test_dtos.py     # LoginRequest 테스트 추가
│   │   │   ├── user/
│   │   │   │   └── test_sqlalchemy_user_repository.py  # update_last_login 테스트 추가
│   │   │   └── shared/
│   │   │       └── test_exceptions.py  # 새 예외 클래스 테스트 추가
│   │   └── integration/
│   │       └── test_auth_login.py
│   └── env.example                  # JWT_SECRET_KEY 추가
│
└── frontend/
    └── src/
        ├── shared/
        │   ├── api/
        │   │   └── authApi.ts       # login() 추가
        │   └── lib/
        │       └── tokenStorage.ts  # 토큰 저장/조회
        ├── features/
        │   └── auth/
        │       ├── types.ts         # LoginFormData 추가
        │       ├── ui/
        │       │   └── LoginForm.tsx
        │       └── lib/
        │           └── validation.ts  # validateLoginForm 추가
        └── pages/
            └── login/
                └── LoginPage.tsx
```

---

### 2.2 API 상세 설계

#### POST /api/v1/auth/login

**Request:**
```http
POST /api/v1/auth/login HTTP/1.1
Host: api.example.com
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c3JfMDFBUlozTkRFS1RTVjRSUkZGNjY5RzVGQVYiLCJleHAiOjE3MDU2NzI4MDAsInR5cGUiOiJhY2Nlc3MifQ...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOiJ1c3JfMDFBUlozTkRFS1RTVjRSUkZGNjY5RzVGQVYiLCJleHAiOjE3MDYyNzc2MDAsInR5cGUiOiJyZWZyZXNoIn0...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

**Response (401 Unauthorized - Invalid Credentials):**
```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "이메일 또는 비밀번호가 올바르지 않습니다."
  }
}
```

**Response (403 Forbidden - Inactive Account):**
```http
HTTP/1.1 403 Forbidden
Content-Type: application/json

{
  "success": false,
  "error": {
    "code": "ACCOUNT_INACTIVE",
    "message": "비활성화된 계정입니다. 고객센터로 문의해주세요."
  }
}
```

---

### 2.3 메소드 시그니처

#### Backend

**JWT Handler (`apps/backend/app/auth/infrastructure/jwt_handler.py`):**
```python
import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: Dict[str, str]) -> str:
    """Access Token 생성
    
    Args:
        data: 토큰에 포함할 데이터 (최소한 "sub": user_uid 포함)
    
    Returns:
        JWT Access Token 문자열
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(uid: str) -> str:
    """Refresh Token 생성
    
    Args:
        uid: 사용자 Business ID (예: "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV")
    
    Returns:
        JWT Refresh Token 문자열
    """
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"uid": uid, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """토큰 검증 및 디코딩
    
    Args:
        token: JWT 토큰 문자열
    
    Returns:
        검증 성공 시 Payload 딕셔너리, 실패 시 None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_token_uid(payload: Dict[str, Any]) -> Optional[str]:
    """Payload에서 사용자 UID 추출
    
    Args:
        payload: JWT Payload 딕셔너리
    
    Returns:
        사용자 UID 또는 None
    """
    return payload.get("sub") or payload.get("uid")
```

**Auth Service (`apps/backend/app/auth/application/services.py`):**
```python
from app.auth.application.dtos import LoginRequest, LoginResponse
from app.auth.infrastructure.jwt_handler import (
    create_access_token,
    create_refresh_token,
)
from app.shared.exceptions import (
    InvalidCredentialsError,
    InactiveAccountError,
    SuspendedAccountError,
)
from app.shared.security import verify_password
from app.user.domain.entities import UserStatus
from app.user.domain.repository import UserRepository

class AuthService:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def login(self, request: LoginRequest) -> LoginResponse:
        """로그인 처리
        
        Args:
            request: 로그인 요청 데이터
        
        Returns:
            Access Token 및 Refresh Token
        
        Raises:
            InvalidCredentialsError: 이메일 또는 비밀번호가 잘못된 경우
            InactiveAccountError: 계정이 비활성화된 경우
            SuspendedAccountError: 계정이 정지된 경우
        """
        # 1. 이메일로 사용자 조회
        user = await self._user_repository.get_by_email(request.email)
        if not user:
            raise InvalidCredentialsError()

        # 2. 계정 상태 확인
        if user.status == UserStatus.INACTIVE:
            raise InactiveAccountError()
        if user.status == UserStatus.SUSPENDED:
            raise SuspendedAccountError()

        # 3. 비밀번호 검증
        if not verify_password(request.password, user.password_hash):
            raise InvalidCredentialsError()

        # 4. 마지막 로그인 시간 업데이트
        await self._user_repository.update_last_login(user.uid)

        # 5. JWT 토큰 생성
        access_token = create_access_token({"sub": user.uid})
        refresh_token = create_refresh_token(user.uid)

        # 6. Refresh Token DB 저장 (추후 구현)
        # await self._token_repository.create(refresh_token, user.id, expires_at)

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=900,  # 15분 = 900초
        )
```

**User Repository (`apps/backend/app/user/domain/repository.py`):**
```python
from typing import Protocol

class UserRepository(Protocol):
    # ... 기존 메소드들 ...
    
    async def update_last_login(self, uid: str) -> None:
        """마지막 로그인 시간 업데이트
        
        Args:
            uid: 사용자 Business ID
        """
        ...
```

**User Repository Implementation (`apps/backend/app/user/infrastructure/repository.py`):**
```python
from datetime import datetime, timezone
from sqlalchemy import update
from app.user.domain.repository import UserRepository
from app.user.domain.entities import User
from app.user.infrastructure.models import UserModel

class SQLAlchemyUserRepository:
    # ... 기존 메소드들 ...
    
    async def update_last_login(self, uid: str) -> None:
        """마지막 로그인 시간 업데이트"""
        stmt = (
            update(UserModel)
            .where(UserModel.uid == uid)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        await self._session.execute(stmt)
        await self._session.commit()
```

**HTTP Router (`apps/backend/app/auth/interface/http/router.py`):**
```python
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.application.dtos import LoginRequest, LoginResponse
from app.auth.application.services import AuthService
from app.shared.database import get_db
from app.shared.exceptions import (
    InvalidCredentialsError,
    InactiveAccountError,
    SuspendedAccountError,
    ValidationError,
)
from app.shared.schemas.response import ApiErrorBody, ApiErrorResponse
from app.user.infrastructure.repository import SQLAlchemyUserRepository

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """AuthService 의존성"""
    return AuthService(SQLAlchemyUserRepository(session))

@router.post(
    "/login",
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="이메일과 비밀번호로 로그인하고 JWT 토큰을 발급받습니다.",
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """로그인 엔드포인트"""
    try:
        response = await auth_service.login(request)
        return {"success": True, "data": response.model_dump()}
    except InvalidCredentialsError as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=ApiErrorResponse(
                error=ApiErrorBody(
                    code=e.code,
                    message=e.message,
                )
            ).model_dump(),
        )
    except (InactiveAccountError, SuspendedAccountError) as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=ApiErrorResponse(
                error=ApiErrorBody(
                    code=e.code,
                    message=e.message,
                )
            ).model_dump(),
        )
    except ValidationError as e:
        details = (
            [ErrorDetail(field=e.field, message=e.message)]
            if e.field
            else None
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=ApiErrorResponse(
                error=ApiErrorBody(
                    code=e.code,
                    message=e.message,
                    details=details,
                )
            ).model_dump(),
        )
```

#### Frontend

**API Client (`apps/frontend/src/shared/api/authApi.ts`):**
```typescript
import { client } from './client';
import { ApiResponse } from '../types/api';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export async function login(
  data: LoginRequest
): Promise<LoginResponse> {
  const response = await client.post<
    ApiResponse<LoginResponse>
  >('/auth/login', data);
  return response.data.data;
}
```

**Token Storage (`apps/frontend/src/shared/lib/tokenStorage.ts`):**
```typescript
const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';

export function setAccessToken(token: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, token);
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setRefreshToken(token: string): void {
  localStorage.setItem(REFRESH_TOKEN_KEY, token);
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}
```

**Login Form (`apps/frontend/src/features/auth/ui/LoginForm.tsx`):**
```typescript
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../../../shared/api/authApi';
import { setAccessToken, setRefreshToken } from '../../../shared/lib/tokenStorage';
import { validateLoginForm } from '../lib/validation';
import { LoginFormData } from '../types';
import { ApiError } from '../../../shared/types/api';

export function LoginForm() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
  });
  const [errors, setErrors] = useState<Partial<LoginFormData>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState<string | null>(null);

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      
      const validationErrors = validateLoginForm(formData);
      if (Object.keys(validationErrors).length > 0) {
        setErrors(validationErrors);
        return;
      }

      setIsLoading(true);
      setServerError(null);

      try {
        const response = await login({
          email: formData.email,
          password: formData.password,
        });
        
        // 토큰 저장
        setAccessToken(response.access_token);
        setRefreshToken(response.refresh_token);
        
        // 메인 페이지로 리다이렉트
        navigate('/');
      } catch (err) {
        const apiError = err as ApiError;
        setServerError(apiError.message || '로그인에 실패했습니다.');
      } finally {
        setIsLoading(false);
      }
    },
    [formData, navigate]
  );

  // ... 나머지 구현 (입력 필드, 에러 표시 등)
}
```

---

### 2.4 데이터베이스 변경사항

로그인 기능은 기존 `users` 테이블을 사용하며, 추가 마이그레이션은 필요하지 않습니다.

**업데이트되는 필드:**
- `last_login_at`: 로그인 성공 시 현재 시간(UTC)으로 업데이트

**Refresh Token 저장 (추후 구현):**
- `refresh_tokens` 테이블에 새 Refresh Token 저장
- 이번 단계에서는 스킵하고, 004-refresh 스펙에서 구현

---

### 2.5 환경 변수

**`apps/backend/env.example`:**
```bash
# JWT 토큰 서명에 사용되는 비밀키 (최소 32바이트 랜덤 문자열)
JWT_SECRET_KEY=your-secret-key-here-minimum-32-bytes
```

---

### 2.6 에러 처리 전략

1. **보안 고려사항**: 존재하지 않는 이메일과 잘못된 비밀번호를 구분하지 않음
   - 둘 다 `InvalidCredentialsError` (401) 반환
   - 동일한 에러 메시지: "이메일 또는 비밀번호가 올바르지 않습니다."

2. **계정 상태별 에러**:
   - `INACTIVE` → `InactiveAccountError` (403)
   - `SUSPENDED` → `SuspendedAccountError` (403)

3. **유효성 검증 에러**:
   - Pydantic 검증 실패 → `ValidationError` (400)
   - 필드별 상세 에러 메시지 제공

---

### 2.7 Rate Limiting

Epic planning에 따르면:
- **POST /auth/login**: 5회/5분 (IP + Email 기준)

이번 단계에서는 Rate Limiting 구현을 스킵하고, 추후 미들웨어로 추가 예정.

---

## 3. 참고사항

- JWT Secret Key는 반드시 환경변수로 관리
- Access Token은 짧게 유지 (15분)하여 탈취 시 피해 최소화
- Refresh Token은 추후 DB에 저장하여 무효화 가능하도록 설계
- `last_login_at`은 UTC 시간으로 저장
- 모든 에러 메시지는 보안을 고려하여 구체적인 정보 노출 최소화
