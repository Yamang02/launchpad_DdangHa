import { test, expect } from '@playwright/test';

/**
 * 예제 테스트 파일
 * TDD 연습을 위한 기본 구조
 */
test.describe('홈페이지', () => {
  test('페이지가 정상적으로 로드되어야 함', async ({ page }) => {
    await page.goto('/');
    
    // 페이지 제목 확인
    await expect(page).toHaveTitle(/DdangHa/);
  });

  test('기본 메시지가 표시되어야 함', async ({ page }) => {
    await page.goto('/');
    
    // 특정 텍스트가 있는지 확인
    await expect(page.getByText('DdangHa Frontend')).toBeVisible();
  });
});
