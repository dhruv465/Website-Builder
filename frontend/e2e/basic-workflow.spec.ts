import { test, expect } from '@playwright/test';

test.describe('Basic Website Builder Workflow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load the application', async ({ page }) => {
    // Check that the main heading is visible
    await expect(page.locator('h1')).toBeVisible();
    
    // Check that the prompt input is visible
    const promptInput = page.locator('textarea, input[type="text"]').first();
    await expect(promptInput).toBeVisible();
  });

  test('should display agent pipeline', async ({ page }) => {
    // Check that agent names are displayed
    await expect(page.getByText(/requirements agent/i)).toBeVisible();
    await expect(page.getByText(/code generation agent/i)).toBeVisible();
    await expect(page.getByText(/audit agent/i)).toBeVisible();
    await expect(page.getByText(/deployment agent/i)).toBeVisible();
  });

  test('should have build button', async ({ page }) => {
    // Check that the build/run button exists
    const buildButton = page.getByRole('button', { name: /build|run|generate/i });
    await expect(buildButton).toBeVisible();
  });

  test('should have tabs for preview, audit, and code', async ({ page }) => {
    // Check for tab buttons
    await expect(page.getByRole('button', { name: /preview/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /audit/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /code/i })).toBeVisible();
  });

  test('should switch between tabs', async ({ page }) => {
    // Click on audit tab
    await page.getByRole('button', { name: /audit/i }).click();
    
    // Verify audit content is visible
    await expect(page.getByText(/run a build to see the audit report/i)).toBeVisible();
    
    // Click on code tab
    await page.getByRole('button', { name: /code/i }).click();
    
    // Verify code content is visible
    await expect(page.getByText(/generated code will appear here/i)).toBeVisible();
    
    // Click back to preview tab
    await page.getByRole('button', { name: /preview/i }).click();
  });

  test('should allow text input in prompt field', async ({ page }) => {
    const promptInput = page.locator('textarea, input[type="text"]').first();
    
    await promptInput.fill('Build me a portfolio website');
    
    await expect(promptInput).toHaveValue(/portfolio website/i);
  });

  test('should have device size toggles', async ({ page }) => {
    // Check for device size buttons (desktop, tablet, mobile)
    const deviceButtons = page.locator('button').filter({ hasText: /desktop|tablet|mobile/i });
    await expect(deviceButtons.first()).toBeVisible();
  });
});
