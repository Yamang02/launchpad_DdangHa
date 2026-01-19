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
