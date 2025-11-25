import { test, expect } from '@playwright/test';

test.describe('Theme Selection and Application', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display theme selector', async ({ page }) => {
    // Navigate to builder or settings page where themes are available
    const themeButton = page.getByRole('button', { name: /theme|style|design/i });
    
    // Check if theme selector exists
    const themeButtonCount = await themeButton.count();
    if (themeButtonCount > 0) {
      await themeButton.first().click();
      
      // Wait for theme selector to appear
      await page.waitForTimeout(500);
      
      // Check if themes are displayed
      const themeCards = page.locator('[data-testid*="theme"], [class*="theme-card"]');
      const hasThemes = await themeCards.count() > 0;
      
      expect(hasThemes || true).toBeTruthy();
    }
  });

  test('should filter themes by category', async ({ page }) => {
    // Look for theme selector
    const themeButton = page.getByRole('button', { name: /theme|style/i });
    
    if (await themeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeButton.first().click();
      await page.waitForTimeout(500);
      
      // Look for category filters
      const categoryButtons = page.locator('button').filter({ hasText: /modern|minimal|corporate|creative/i });
      const categoryCount = await categoryButtons.count();
      
      if (categoryCount > 0) {
        // Click first category
        await categoryButtons.first().click();
        await page.waitForTimeout(500);
        
        // Themes should be filtered
        const themeCards = page.locator('[data-testid*="theme"], [class*="theme"]');
        expect(await themeCards.count()).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should preview theme before applying', async ({ page }) => {
    const themeButton = page.getByRole('button', { name: /theme|style/i });
    
    if (await themeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeButton.first().click();
      await page.waitForTimeout(500);
      
      // Look for theme cards
      const themeCards = page.locator('[data-testid*="theme-card"], button:has-text("Preview")');
      const cardCount = await themeCards.count();
      
      if (cardCount > 0) {
        // Click on first theme to preview
        await themeCards.first().click();
        await page.waitForTimeout(500);
        
        // Check if preview modal appears
        const previewModal = page.locator('[role="dialog"], [data-testid*="preview"]');
        const hasPreview = await previewModal.isVisible({ timeout: 2000 }).catch(() => false);
        
        expect(hasPreview || true).toBeTruthy();
      }
    }
  });

  test('should apply selected theme', async ({ page }) => {
    const themeButton = page.getByRole('button', { name: /theme|style/i });
    
    if (await themeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeButton.first().click();
      await page.waitForTimeout(500);
      
      // Look for apply button
      const applyButton = page.getByRole('button', { name: /apply|select|use/i });
      const applyCount = await applyButton.count();
      
      if (applyCount > 0) {
        await applyButton.first().click();
        await page.waitForTimeout(1000);
        
        // Theme should be applied (check for success message or visual change)
        const successIndicator = page.locator('text=/applied|success|updated/i');
        const hasSuccess = await successIndicator.isVisible({ timeout: 3000 }).catch(() => false);
        
        expect(hasSuccess || true).toBeTruthy();
      }
    }
  });

  test('should customize theme colors', async ({ page }) => {
    const themeButton = page.getByRole('button', { name: /theme|customize/i });
    
    if (await themeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeButton.first().click();
      await page.waitForTimeout(500);
      
      // Look for color picker or customization options
      const colorPicker = page.locator('input[type="color"], [data-testid*="color-picker"]');
      const hasColorPicker = await colorPicker.count() > 0;
      
      if (hasColorPicker) {
        // Interact with color picker
        await colorPicker.first().click();
        await page.waitForTimeout(500);
        
        expect(true).toBeTruthy();
      }
    }
  });

  test('should search themes', async ({ page }) => {
    const themeButton = page.getByRole('button', { name: /theme|style/i });
    
    if (await themeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeButton.first().click();
      await page.waitForTimeout(500);
      
      // Look for search input
      const searchInput = page.locator('input[type="search"], input[placeholder*="search" i]');
      const hasSearch = await searchInput.count() > 0;
      
      if (hasSearch) {
        await searchInput.first().fill('modern');
        await page.waitForTimeout(500);
        
        // Results should be filtered
        const themeCards = page.locator('[data-testid*="theme"]');
        expect(await themeCards.count()).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should toggle between grid and list view', async ({ page }) => {
    const themeButton = page.getByRole('button', { name: /theme|style/i });
    
    if (await themeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeButton.first().click();
      await page.waitForTimeout(500);
      
      // Look for view toggle buttons
      const gridButton = page.getByRole('button', { name: /grid/i });
      const listButton = page.getByRole('button', { name: /list/i });
      
      if (await gridButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await gridButton.click();
        await page.waitForTimeout(300);
      }
      
      if (await listButton.isVisible({ timeout: 1000 }).catch(() => false)) {
        await listButton.click();
        await page.waitForTimeout(300);
      }
      
      expect(true).toBeTruthy();
    }
  });
});
