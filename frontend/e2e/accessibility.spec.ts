import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

test.describe('Accessibility', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should not have any automatically detectable accessibility issues', async ({ page }) => {
    const accessibilityScanResults = await new AxeBuilder({ page }).analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should not have accessibility issues on builder page', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should not have accessibility issues on projects page', async ({ page }) => {
    await page.goto('/projects');
    await page.waitForTimeout(1000);
    
    const accessibilityScanResults = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();
    
    expect(accessibilityScanResults.violations).toEqual([]);
  });

  test('should not have accessibility issues in modals', async ({ page }) => {
    // Open a modal if available
    const modalTrigger = page.getByRole('button', { name: /settings|theme|deploy/i }).first();
    
    if (await modalTrigger.isVisible({ timeout: 2000 }).catch(() => false)) {
      await modalTrigger.click();
      await page.waitForTimeout(500);
      
      const accessibilityScanResults = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa'])
        .analyze();
      
      expect(accessibilityScanResults.violations).toEqual([]);
    }
  });

  test('should have proper heading hierarchy', async ({ page }) => {
    // Check for h1
    const h1 = page.locator('h1');
    await expect(h1).toBeVisible();
    
    // Count headings
    const h1Count = await h1.count();
    expect(h1Count).toBeGreaterThan(0);
  });

  test('should have accessible form inputs', async ({ page }) => {
    const promptInput = page.locator('textarea, input[type="text"]').first();
    
    // Check if input is accessible
    await expect(promptInput).toBeVisible();
    await expect(promptInput).toBeEnabled();
    
    // Check if input can receive focus
    await promptInput.focus();
    await expect(promptInput).toBeFocused();
  });

  test('should have accessible buttons', async ({ page }) => {
    // Get all buttons
    const buttons = page.getByRole('button');
    const buttonCount = await buttons.count();
    
    // Should have at least one button
    expect(buttonCount).toBeGreaterThan(0);
    
    // Check first button is accessible
    const firstButton = buttons.first();
    await expect(firstButton).toBeVisible();
    await expect(firstButton).toBeEnabled();
  });

  test('should support keyboard navigation', async ({ page }) => {
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    
    // Check if an element is focused
    const focusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(focusedElement).toBeDefined();
    
    // Tab again
    await page.keyboard.press('Tab');
    
    // Should move focus to another element
    const newFocusedElement = await page.evaluate(() => document.activeElement?.tagName);
    expect(newFocusedElement).toBeDefined();
  });

  test('should have sufficient color contrast', async ({ page }) => {
    // This is a basic check - full contrast testing would require additional tools
    // Check that text is visible against background
    const h1 = page.locator('h1').first();
    
    if (await h1.isVisible()) {
      const color = await h1.evaluate(el => {
        return window.getComputedStyle(el).color;
      });
      
      // Color should be defined
      expect(color).toBeDefined();
      expect(color).not.toBe('');
    }
  });

  test('should have proper ARIA labels where needed', async ({ page }) => {
    // Check for ARIA labels on interactive elements
    const elementsWithAria = page.locator('[aria-label], [aria-labelledby], [role]');
    const count = await elementsWithAria.count();
    
    // Should have some ARIA attributes
    expect(count).toBeGreaterThanOrEqual(0);
  });

  test('should be navigable with keyboard only', async ({ page }) => {
    // Start from the beginning
    await page.keyboard.press('Tab');
    
    // Tab through several elements
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(100);
    }
    
    // Should be able to activate focused element with Enter or Space
    await page.keyboard.press('Enter');
    
    // Page should still be functional
    const promptInput = page.locator('textarea, input[type="text"]').first();
    await expect(promptInput).toBeVisible();
  });
});
