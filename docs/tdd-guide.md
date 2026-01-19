# TDD 가이드

본 문서는 **Playwright (Frontend)**와 **pytest (Backend)**를 이용한 **TDD (Test-Driven Development)** 연습 가이드입니다.

빌더톤 환경에 맞춰 **실용적이고 간단한** TDD 워크플로우를 제안합니다.

---

## TDD란?

**Test-Driven Development (테스트 주도 개발)**는 다음 순서로 개발하는 방법론입니다:

1. **Red**: 실패하는 테스트 작성
2. **Green**: 테스트를 통과하는 최소한의 코드 작성
3. **Refactor**: 코드 개선 (테스트는 계속 통과)

---

## 목차

- [Frontend TDD (Playwright)](#frontend-tdd-playwright)
- [Backend TDD (pytest + FastAPI)](#backend-tdd-pytest--fastapi)

---

## Frontend TDD (Playwright)

### Playwright TDD 워크플로우

### 1. 테스트 작성 (Red 단계)

먼저 **사용자 관점에서** 원하는 동작을 테스트로 작성합니다.

**예시: 사용자 로그인 기능**

```typescript
// e2e/auth/login.spec.ts
import { test, expect } from '@playwright/test';

test.describe('사용자 로그인', () => {
  test('올바른 이메일과 비밀번호로 로그인할 수 있어야 함', async ({ page }) => {
    await page.goto('/login');
    
    // 이메일 입력
    await page.fill('input[name="email"]', 'user@example.com');
    
    // 비밀번호 입력
    await page.fill('input[name="password"]', 'password123');
    
    // 로그인 버튼 클릭
    await page.click('button[type="submit"]');
    
    // 로그인 성공 확인
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('환영합니다')).toBeVisible();
  });

  test('잘못된 이메일/비밀번호로 로그인 시 에러 메시지 표시', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="email"]', 'wrong@example.com');
    await page.fill('input[name="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // 에러 메시지 확인
    await expect(page.getByText('이메일 또는 비밀번호가 올바르지 않습니다')).toBeVisible();
  });
});
```

### 2. 테스트 실행 (Red 확인)

테스트를 실행하여 **실패하는 것을 확인**합니다.

```bash
# Frontend 디렉토리에서
cd apps/frontend
yarn test:e2e
```

또는 UI 모드로 실행:

```bash
yarn test:e2e:ui
```

### 3. 최소한의 구현 (Green 단계)

테스트를 통과시키기 위한 **최소한의 코드**만 작성합니다.

**예시: 로그인 페이지 구현**

```typescript
// src/pages/login/LoginPage.tsx
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // 간단한 검증 (나중에 API 연동)
    if (email === 'user@example.com' && password === 'password123') {
      navigate('/dashboard');
    } else {
      setError('이메일 또는 비밀번호가 올바르지 않습니다');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        name="email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        name="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      {error && <p>{error}</p>}
      <button type="submit">로그인</button>
    </form>
  );
};
```

### 4. 테스트 재실행 (Green 확인)

테스트가 통과하는지 확인합니다.

```bash
yarn test:e2e
```

### 5. 리팩토링 (Refactor 단계)

코드를 개선하되, **테스트는 계속 통과**해야 합니다.

- 코드 중복 제거
- 함수 분리
- 네이밍 개선
- 구조 개선

---

## TDD 연습 시작하기

### 단계별 추천 순서

#### 1단계: 기본 UI 테스트
- 페이지 로드 확인
- 텍스트 표시 확인
- 버튼 클릭 확인

**예시:**
```typescript
test('홈페이지가 정상적으로 표시되어야 함', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('DdangHa')).toBeVisible();
});
```

#### 2단계: 폼 입력 테스트
- 입력 필드 채우기
- 제출 버튼 클릭
- 검증 메시지 확인

**예시:**
```typescript
test('이메일 입력 폼이 동작해야 함', async ({ page }) => {
  await page.goto('/contact');
  await page.fill('input[name="email"]', 'test@example.com');
  await expect(page.locator('input[name="email"]')).toHaveValue('test@example.com');
});
```

#### 3단계: 네비게이션 테스트
- 링크 클릭
- 페이지 이동 확인
- URL 변경 확인

**예시:**
```typescript
test('로그인 후 대시보드로 이동해야 함', async ({ page }) => {
  await page.goto('/login');
  // 로그인 로직...
  await expect(page).toHaveURL('/dashboard');
});
```

#### 4단계: API 연동 테스트
- API 호출 모킹
- 응답 처리 확인
- 에러 처리 확인

**예시:**
```typescript
test('API 호출 후 데이터가 표시되어야 함', async ({ page }) => {
  // API 응답 모킹
  await page.route('**/api/users', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify([{ id: 1, name: 'Test User' }])
    });
  });

  await page.goto('/users');
  await expect(page.getByText('Test User')).toBeVisible();
});
```

---

## Playwright 유용한 기능

### 1. 페이지 객체 패턴 (Page Object Model)

반복되는 셀렉터와 액션을 재사용 가능한 객체로 분리합니다.

```typescript
// e2e/pages/LoginPage.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('input[name="email"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.submitButton = page.locator('button[type="submit"]');
    this.errorMessage = page.locator('.error-message');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}

// 사용 예시
test('로그인 테스트', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.login('user@example.com', 'password123');
  await expect(page).toHaveURL('/dashboard');
});
```

### 2. Fixture 활용

공통 설정이나 데이터를 재사용합니다.

```typescript
// e2e/fixtures/auth.ts
import { test as base } from '@playwright/test';

type AuthFixtures = {
  authenticatedPage: Page;
};

export const test = base.extend<AuthFixtures>({
  authenticatedPage: async ({ page }, use) => {
    // 로그인 로직
    await page.goto('/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.waitForURL('/dashboard');
    
    await use(page);
  },
});

// 사용 예시
test('인증된 사용자가 대시보드를 볼 수 있어야 함', async ({ authenticatedPage }) => {
  await authenticatedPage.goto('/dashboard');
  await expect(authenticatedPage.getByText('환영합니다')).toBeVisible();
});
```

### 3. API 모킹

실제 API 없이 테스트할 수 있습니다.

```typescript
test('사용자 목록이 표시되어야 함', async ({ page }) => {
  // API 응답 모킹
  await page.route('**/api/v1/users', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: '사용자1', email: 'user1@example.com' },
        { id: 2, name: '사용자2', email: 'user2@example.com' },
      ]),
    });
  });

  await page.goto('/users');
  await expect(page.getByText('사용자1')).toBeVisible();
  await expect(page.getByText('사용자2')).toBeVisible();
});
```

---

## TDD 모범 사례

### 1. 작은 단위로 시작
- 한 번에 하나의 기능만 테스트
- 복잡한 테스트는 여러 개의 작은 테스트로 분리

### 2. 사용자 관점에서 작성
- "사용자가 무엇을 할 수 있어야 하는가?"
- 기술적 세부사항보다 사용자 행동에 집중

### 3. 명확한 테스트 이름
```typescript
// Good
test('올바른 이메일과 비밀번호로 로그인할 수 있어야 함', ...)

// Bad
test('로그인 테스트', ...)
```

### 4. 독립적인 테스트
- 각 테스트는 다른 테스트에 의존하지 않아야 함
- 테스트 순서가 바뀌어도 동일하게 동작

### 5. 실패 메시지 확인
- 테스트가 실패했을 때 왜 실패했는지 명확히 알 수 있어야 함
- `expect`에 의미 있는 메시지 추가

---

## 실행 명령어

```bash
# 모든 테스트 실행
yarn test:e2e

# UI 모드로 실행 (추천)
yarn test:e2e:ui

# 디버그 모드
yarn test:e2e:debug

# 헤드 모드 (브라우저 표시)
yarn test:e2e:headed

# 특정 테스트 파일만 실행
yarn test:e2e e2e/auth/login.spec.ts

# 특정 브라우저만 실행
yarn test:e2e --project=chromium
```

---

## 디렉토리 구조

```
apps/frontend/
  e2e/
    pages/           # Page Object Model
      LoginPage.ts
      DashboardPage.ts
    fixtures/         # 공통 Fixture
      auth.ts
    auth/            # 인증 관련 테스트
      login.spec.ts
      logout.spec.ts
    users/            # 사용자 관련 테스트
      user-list.spec.ts
      user-profile.spec.ts
    example.spec.ts   # 예제 테스트
```

---

## TDD 연습 시나리오 추천

### 초급: 기본 UI 테스트
1. 홈페이지 로드 테스트
2. 네비게이션 메뉴 클릭 테스트
3. 폼 입력 및 제출 테스트

### 중급: 사용자 플로우 테스트
1. 회원가입 → 로그인 → 대시보드 플로우
2. 상품 목록 → 상세 → 장바구니 추가 플로우
3. 검색 → 필터 → 정렬 플로우

### 고급: 복잡한 상호작용 테스트
1. 실시간 검색 (debounce)
2. 무한 스크롤
3. 드래그 앤 드롭
4. 파일 업로드

---

## 문제 해결

### 테스트가 불안정할 때
- `waitFor` 사용하여 요소가 나타날 때까지 대기
- `toHaveURL` 대신 `waitForURL` 사용
- 네트워크 요청 완료 대기

### 느린 테스트
- 병렬 실행 활용 (`fullyParallel: true`)
- 불필요한 대기 시간 제거
- API 모킹으로 실제 네트워크 요청 최소화

---

## 정리

TDD는 **작은 단계로 나누어** 개발하는 습관을 기르는 것이 중요합니다.

**기억할 점:**
1. 테스트 먼저 작성 (Red)
2. 최소한의 코드로 통과 (Green)
3. 코드 개선 (Refactor)
4. 반복

빌더톤 환경에서는 **핵심 기능만** TDD로 작성하고, 나머지는 필요에 따라 추가합니다.
