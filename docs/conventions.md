# 개발 컨벤션

본 문서는 **launchpad (DdangHa)** 프로젝트의 개발 컨벤션을 정의한다.

빌더톤 환경에 맞춰 **실용적이고 간단한** 규칙을 우선한다.

---

## Git 컨벤션

### 브랜치 전략

- `main`: 프로덕션 배포용 (보호)
- `dev`: 개발 통합 브랜치
- `feature/{domain-name}`: 기능 개발 브랜치
  - 예: `feature/user-auth`, `feature/payment`

**원칙:**
- 작은 단위로 자주 머지
- 충돌 발생 시 즉시 해결
- 빌더톤 기간에는 복잡한 브랜치 전략 지양

### 커밋 메시지

**형식:**
```
<type>: <subject>

<body> (optional)
```

**Type:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드/설정 변경

**예시:**
```
feat: user authentication with JWT
fix: database connection timeout issue
docs: update API endpoint documentation
refactor: simplify user domain logic
```

**원칙:**
- 한 커밋 = 하나의 논리적 변경
- 제목은 50자 이내
- 본문은 "무엇을", "왜" 변경했는지 설명

---

## 네이밍 컨벤션

### Backend (Python)

**파일/모듈:**
- `snake_case`
- 예: `user_service.py`, `auth_handler.py`

**클래스:**
- `PascalCase`
- 예: `UserService`, `AuthHandler`

**함수/변수:**
- `snake_case`
- 예: `get_user_by_id()`, `user_id`

**상수:**
- `UPPER_SNAKE_CASE`
- 예: `MAX_RETRY_COUNT`, `DEFAULT_TIMEOUT`

**프라이빗 멤버:**
- `_single_leading_underscore`
- 예: `_internal_method()`, `_cache_data`

### Frontend (TypeScript/React)

**파일/디렉토리:**
- `PascalCase` (컴포넌트)
- `camelCase` (유틸리티, 훅)
- 예: `UserProfile.tsx`, `useAuth.ts`, `apiClient.ts`

**컴포넌트:**
- `PascalCase`
- 예: `UserProfile`, `LoginForm`

**함수/변수:**
- `camelCase`
- 예: `getUserData()`, `userId`

**상수:**
- `UPPER_SNAKE_CASE`
- 예: `API_BASE_URL`, `MAX_ITEMS`

**타입/인터페이스:**
- `PascalCase`
- 예: `User`, `ApiResponse<T>`

**커스텀 훅:**
- `use` 접두사
- 예: `useAuth()`, `useUserData()`

### 데이터베이스

**테이블:**
- `snake_case`, 복수형
- 예: `users`, `user_sessions`, `payment_transactions`

**컬럼:**
- `snake_case`
- 예: `user_id`, `created_at`, `is_active`

**인덱스:**
- `idx_{table}_{columns}`
- 예: `idx_users_email`, `idx_payments_user_id`

### API 엔드포인트

**RESTful:**
- `kebab-case`
- 리소스 중심
- 예: `/api/v1/users`, `/api/v1/users/{id}`, `/api/v1/payments/{id}/refund`

**HTTP 메서드:**
- `GET`: 조회
- `POST`: 생성
- `PUT`: 전체 수정
- `PATCH`: 부분 수정
- `DELETE`: 삭제

---

## 코드 스타일

### Backend (Python)

**최상위 패키지:** `app` (FastAPI 표준). Import: `from app.shared.uid import ...`

**포맷터:**
- `ruff format` (Black 호환)

**린터:**
- `ruff check`

**타입 힌팅:**
- 모든 공개 함수/메서드에 타입 힌트 필수
- 예:
```python
def get_user(user_id: int) -> User | None:
    ...
```

**Docstring:**
- Google 스타일 (간단하게)
- 공개 API에만 필수
```python
def create_user(email: str, password: str) -> User:
    """사용자를 생성합니다.
    
    Args:
        email: 사용자 이메일
        password: 비밀번호
        
    Returns:
        생성된 User 객체
        
    Raises:
        ValueError: 이메일 형식이 올바르지 않은 경우
    """
```

**Import 순서:**
1. 표준 라이브러리
2. 서드파티 라이브러리
3. 로컬 모듈

**예외 처리:**
- 구체적인 예외 타입 사용
- 커스텀 예외는 도메인별로 정의
```python
class UserNotFoundError(Exception):
    """사용자를 찾을 수 없을 때 발생"""
    pass
```

### Frontend (TypeScript/React)

**포맷터:**
- Prettier (Vite 기본 설정)

**린터:**
- ESLint (기존 설정 유지)

**타입:**
- `any` 사용 금지
- 명시적 타입 선언 우선
```typescript
// Good
const userId: number = 1;
const user: User | null = await fetchUser(userId);

// Bad
const userId: any = 1;
```

**컴포넌트:**
- 함수형 컴포넌트만 사용
- Props는 인터페이스로 정의
```typescript
interface UserProfileProps {
  userId: number;
  showEmail?: boolean;
}

export const UserProfile: React.FC<UserProfileProps> = ({ userId, showEmail = false }) => {
  // ...
};
```

**Hooks:**
- 커스텀 훅은 `use` 접두사
- 의존성 배열 정확히 명시
```typescript
useEffect(() => {
  // ...
}, [userId, showEmail]);
```

---

## 파일/디렉토리 구조

### Backend

**도메인별 구조:**
```
src/
  domain/
    user/
      __init__.py
      models.py          # 도메인 모델
      repository.py      # 인터페이스
  application/
    user/
      usecases.py        # 유스케이스
      services.py        # 애플리케이션 서비스
  interface/
    http/
      routers/
        user.py          # FastAPI 라우터
  infrastructure/
    db/
      repositories/
        user_repository.py  # 구현체
```

**파일 명명:**
- 한 파일 = 하나의 주요 개념
- 파일 크기: 200줄 이내 권장 (빌더톤에서는 유연하게)

### Frontend (FSD)

**레이어별 구조:**
```
src/
  shared/          # 공통 유틸리티
    lib/
    ui/
    api/
  entities/        # 비즈니스 엔티티
    user/
      model/
      ui/
  features/        # 사용자 기능
    auth/
      login/
      logout/
  widgets/         # 복합 UI 블록
    header/
    sidebar/
  pages/           # 페이지
    home/
    profile/
  app/             # 앱 설정
    providers/
    router/
```

**FSD 규칙:**
- 상위 레이어는 하위 레이어만 import
- 같은 레이어 간 import 가능
- Public API만 export (`index.ts`)

---

## API 컨벤션

### 응답 형식

**성공:**
```json
{
  "data": { ... },
  "message": "Success"
}
```

**에러:**
```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "사용자를 찾을 수 없습니다",
    "details": { ... }
  }
}
```

### HTTP 상태 코드

- `200`: 성공
- `201`: 생성 성공
- `400`: 잘못된 요청
- `401`: 인증 실패
- `403`: 권한 없음
- `404`: 리소스 없음
- `500`: 서버 오류

### 버전 관리

- URL에 버전 포함: `/api/v1/...`
- Breaking change 시 버전 업데이트

---

## 에러 처리

### Backend

**예외 계층:**
```python
# 도메인 예외
class DomainError(Exception):
    """도메인 로직 오류"""
    pass

class UserNotFoundError(DomainError):
    pass

# 애플리케이션 예외
class ApplicationError(Exception):
    """애플리케이션 레벨 오류"""
    pass
```

**FastAPI 에러 핸들러:**
- 전역 에러 핸들러로 일관된 응답 형식 유지

### Frontend

**에러 처리:**
- API 호출은 try-catch로 감싸기
- 사용자 친화적 메시지 표시
- 에러 로깅 (개발 환경)

```typescript
try {
  const user = await api.getUser(userId);
} catch (error) {
  if (error instanceof ApiError) {
    showToast(error.message);
  } else {
    console.error('Unexpected error:', error);
  }
}
```

---

## 문서화

### 코드 주석

- **Why** 중심 (What은 코드로 설명)
- 복잡한 로직에만 주석
- TODO는 이슈로 추적

### API 문서

- FastAPI 자동 생성 문서 활용 (`/docs`)
- 주요 엔드포인트는 README에 예시 포함

### README

- 각 도메인/기능별 README는 선택사항
- 복잡한 로직만 문서화

---

## 테스트

### 원칙

- **빌더톤 기간에는 선택사항**
- 핵심 비즈니스 로직만 테스트
- E2E 테스트는 데모용으로만

### Backend

- `pytest` 사용
- 테스트 파일: `test_*.py` 또는 `*_test.py`
- Fixture는 `conftest.py`에 정의

### Frontend

- 테스트는 선택사항
- 필요시 Vitest 사용

---

## 환경 변수

### 명명

- `UPPER_SNAKE_CASE`
- 접두사로 그룹화
- 예: `DATABASE_URL`, `API_SECRET_KEY`, `REDIS_HOST`

### 관리

- `.env.example`에 예시 제공
- 실제 값은 `.env` (gitignore)
- 환경별로 분리: `.env.dev`, `.env.main`

---

## 시간 (Datetime) 컨벤션

### 원칙

> **"저장은 UTC, 표시는 로컬"**

| 상황 | 포맷 | 예시 |
|------|------|------|
| DB 저장 | UTC (TIMESTAMP WITH TIME ZONE) | `2025-01-19T15:30:00Z` |
| API 요청/응답 | ISO 8601 (UTC) | `2025-01-19T15:30:00Z` |
| 로그 | ISO 8601 (UTC) | `2025-01-19T15:30:00.123Z` |
| 사용자 표시 | KST (Asia/Seoul) | `2025-01-20 00:30:00` |

### Backend (Python)

```python
from datetime import datetime, timezone

# 현재 시각 (UTC)
now_utc = datetime.now(timezone.utc)

# DB 저장 시 항상 UTC
user.created_at = datetime.now(timezone.utc)

# API 응답 시 ISO 8601 형식
response = {
    "created_at": user.created_at.isoformat()  # "2025-01-19T15:30:00+00:00"
}
```

**금지 사항:**
```python
# Bad - 타임존 없는 datetime
datetime.now()  # naive datetime, 사용 금지!
datetime.utcnow()  # deprecated in Python 3.12+

# Good - 항상 타임존 명시
datetime.now(timezone.utc)
```

### Frontend (TypeScript)

```typescript
// API 응답의 UTC 시간을 KST로 변환하여 표시
const formatToKST = (utcString: string): string => {
  return new Intl.DateTimeFormat('ko-KR', {
    timeZone: 'Asia/Seoul',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(utcString));
};

// 예: "2025-01-19T15:30:00Z" → "2025. 01. 20. 00:30"
```

### Database (PostgreSQL)

```sql
-- 컬럼 정의: 항상 TIMESTAMP WITH TIME ZONE 사용
created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()

-- DB는 UTC로 저장하되, 필요시 변환
SELECT created_at AT TIME ZONE 'Asia/Seoul' AS created_at_kst FROM users;
```

### 타임존 참조

| 약어 | 이름 | UTC 오프셋 | 비고 |
|------|------|-----------|------|
| UTC | Coordinated Universal Time | +00:00 | 기준 시간 |
| KST | Korea Standard Time | +09:00 | Asia/Seoul |

**참고:** IANA 타임존 데이터베이스의 `Asia/Seoul` 사용 권장 (DST 변경 대응)

---

## ID 생성 전략

### 원칙: DB ID와 Business ID 분리

| 구분 | DB ID | Business ID (uid) |
|------|-------|-------------------|
| 용도 | 내부 참조, FK 관계 | 외부 노출, API 응답 |
| 형식 | `BIGSERIAL` (auto increment) | `ULID` with prefix |
| 노출 | 절대 외부 노출 금지 | URL, 응답에서 사용 |
| 예시 | `id = 1` | `uid = "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"` |

### ULID (Universally Unique Lexicographically Sortable Identifier)

**선택 이유:**
- 타임스탬프 기반으로 **시간순 정렬 가능** (인덱싱 효율)
- 분산 환경에서 **머신 ID 조정 불필요** (Lambda 환경에 적합)
- 26자 문자열로 **URL-safe** (Crockford's Base32)
- UUID보다 짧고 가독성 좋음

**구조:**
```
 01ARZ3NDEKTSV4RRFFQ69G5FAV
 |----------|------------|
 Timestamp   Randomness
 (48 bits)   (80 bits)
 10자         16자
```

### Prefix 규칙

각 도메인의 Business ID는 prefix로 타입을 구분합니다:

| 도메인 | Prefix | 예시 |
|--------|--------|------|
| User | `usr_` | `usr_01ARZ3NDEKTSV4RRFFQ69G5FAV` |
| RefreshToken | `rtk_` | `rtk_01ARZ3NDEKTSV4RRFFQ69G5FAV` |
| Payment | `pay_` | `pay_01ARZ3NDEKTSV4RRFFQ69G5FAV` |
| Order | `ord_` | `ord_01ARZ3NDEKTSV4RRFFQ69G5FAV` |

### 사용 예시 (Python)

```python
# backend/app/shared/uid.py
import ulid

def generate_uid(prefix: str) -> str:
    """prefix가 붙은 ULID 생성"""
    return f"{prefix}{ulid.new().str}"

# 사용
user_uid = generate_uid("usr_")  # "usr_01ARZ3NDEKTSV4RRFFQ69G5FAV"
token_uid = generate_uid("rtk_")  # "rtk_01ARZ3NDEKTSV4RRFFQ69G5FAV"
```

### ID 사용 가이드라인

| 상황 | 사용할 ID |
|------|-----------|
| API 요청/응답 | `uid` (Business ID) |
| URL 경로 파라미터 | `uid` (Business ID) |
| JWT 토큰 payload | `uid` (Business ID) |
| DB 조인, FK 관계 | `id` (DB ID) |
| 내부 로깅 (민감) | `id` (DB ID) |
| 외부 로깅, 모니터링 | `uid` (Business ID) |

---

## 로깅

### Backend

- Python `logging` 모듈 사용
- 레벨: DEBUG, INFO, WARNING, ERROR
- 구조화된 로그 (JSON 형식 권장)

```python
import logging

logger = logging.getLogger(__name__)

logger.info("User created", extra={"user_id": user_id, "email": email})
```

### Frontend

- 개발 환경: `console.log`, `console.error`
- 프로덕션: 에러만 로깅
- Sentry 등 에러 트래킹 도구는 선택사항

---

## 정리

이 컨벤션은 **가이드라인**이며, 빌더톤 환경에서는 유연하게 적용한다.

**우선순위:**
1. 코드 동작
2. 가독성
3. 일관성
4. 완벽한 컨벤션 준수

팀원 간 합의가 필요한 경우, 이 문서를 업데이트한다.
