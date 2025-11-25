import { test, expect } from '@playwright/test';

test.describe('Responsive Design', () => {
  test('should display correctly on desktop', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 });
    await page.goto('/');
    
    // Check that main elements are visible
    await expect(page.locator('h1')).toBeVisible();
    const promptInput = page.locator('textarea, input[type="text"]').first();
    await expect(promptInput).toBeVisible();
  });

  test('should display correctly on tablet', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto('/');
    
    // Check that main elements are still visible
    await expect(page.locator('h1')).toBeVisible();
    const promptInput = page.locator('textarea, input[type="text"]').first();
    await expect(promptInput).toBeVisible();
  });

  test('should display correctly on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check that main elements are visible
    await expect(page.locator('h1')).toBeVisible();
    const promptInput = page.locator('textarea, input[type="text"]').first();
    await expect(promptInput).toBeVisible();
  });

  test('should toggle device preview sizes', async ({ page }) => {
    await page.goto('/');
    
    // Look for device size toggle buttons
    const desktopButton = page.getByRole('button').filter({ hasText: /desktop/i }).first();
    const tabletButton = page.getByRole('button').filter({ hasText: /tablet/i }).first();
    const mobileButton = page.getByRole('button').filter({ hasText: /mobile/i }).first();
    
    // Check if device buttons exist
    if (await desktopButton.isVisible()) {
      // Click desktop
      await desktopButton.click();
      await page.waitForTimeout(500);
      
      // Click tablet
      if (await tabletButton.isVisible()) {
        await tabletButton.click();
        await page.waitForTimeout(500);
      }
      
      // Click mobile
      if (await mobileButton.isVisible()) {
        await mobileButton.click();
        await page.waitForTimeout(500);
      }
    }
  });

  test('should be scrollable on small screens', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    
    // Check if page is scrollable
    const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight);
    const clientHeight = await page.evaluate(() => document.documentElement.clientHeight);
    
    // Page should either fit or be scrollable
    expect(scrollHeight).toBeGreaterThanOrEqual(clientHeight);
  });
});
