import { test, expect } from '@playwright/test'

test.describe('회원가입 페이지', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/signup')
  })

  test('회원가입 폼이 올바르게 렌더링됨', async ({ page }) => {
    await expect(page.getByRole('heading', { name: '회원가입' })).toBeVisible()
    await expect(page.getByLabel('이메일')).toBeVisible()
    await expect(page.getByLabel('비밀번호', { exact: true })).toBeVisible()
    await expect(page.getByLabel('비밀번호 확인')).toBeVisible()
    await expect(page.getByLabel('닉네임')).toBeVisible()
    await expect(page.getByRole('button', { name: '회원가입' })).toBeVisible()
    await expect(page.getByRole('link', { name: '로그인' })).toBeVisible()
  })

  test('유효한 정보 입력 시 회원가입 성공 후 로그인 페이지로 이동', async ({
    page,
  }) => {
    const email = `e2e-${Date.now()}@example.com`
    await page.getByLabel('이메일').fill(email)
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123')
    await page.getByLabel('비밀번호 확인').fill('securePassword123')
    await page.getByLabel('닉네임').fill('새로운유저')
    await page.getByRole('button', { name: '회원가입' }).click()

    await expect(page).toHaveURL('/login')
    await expect(
      page.getByText('회원가입이 완료되었습니다. 로그인해주세요.')
    ).toBeVisible()
  })

  test('이메일 형식 오류 시 에러 메시지 표시', async ({ page }) => {
    await page.getByLabel('이메일').fill('invalid-email')
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123')
    await page.getByLabel('비밀번호 확인').fill('securePassword123')
    await page.getByLabel('닉네임').fill('테스트')
    await page.getByRole('button', { name: '회원가입' }).click()

    await expect(
      page.getByText('올바른 이메일 형식이 아닙니다.')
    ).toBeVisible()
  })

  test('비밀번호 규칙 미충족 시 에러 메시지 표시', async ({ page }) => {
    await page.getByLabel('이메일').fill('test@example.com')
    await page.getByLabel('비밀번호', { exact: true }).fill('short')
    await page.getByLabel('비밀번호 확인').fill('short')
    await page.getByLabel('닉네임').fill('테스트')
    await page.getByRole('button', { name: '회원가입' }).click()

    await expect(
      page.getByText('비밀번호는 8자 이상이어야 합니다.')
    ).toBeVisible()
  })

  test('비밀번호 확인 불일치 시 에러 메시지 표시', async ({ page }) => {
    await page.getByLabel('이메일').fill('test@example.com')
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123')
    await page.getByLabel('비밀번호 확인').fill('differentPassword123')
    await page.getByLabel('닉네임').fill('테스트')
    await page.getByRole('button', { name: '회원가입' }).click()

    await expect(page.getByText('비밀번호가 일치하지 않습니다.')).toBeVisible()
  })

  test('중복 이메일 시 에러 메시지 표시', async ({ page }) => {
    const email = `dup-e2e-${Date.now()}@example.com`
    await page.getByLabel('이메일').fill(email)
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123')
    await page.getByLabel('비밀번호 확인').fill('securePassword123')
    await page.getByLabel('닉네임').fill('첫가입')
    await page.getByRole('button', { name: '회원가입' }).click()
    await expect(page).toHaveURL('/login')

    await page.goto('/signup')
    await page.getByLabel('이메일').fill(email)
    await page.getByLabel('비밀번호', { exact: true }).fill('securePassword123')
    await page.getByLabel('비밀번호 확인').fill('securePassword123')
    await page.getByLabel('닉네임').fill('재가입시도')
    await page.getByRole('button', { name: '회원가입' }).click()

    await expect(page.getByText('이미 사용 중인 이메일입니다.')).toBeVisible()
  })

  test('로그인 링크 클릭 시 로그인 페이지로 이동', async ({ page }) => {
    await page.getByRole('link', { name: '로그인' }).click()

    await expect(page).toHaveURL('/login')
  })
})
