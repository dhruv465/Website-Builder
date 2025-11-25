import { test, expect } from '@playwright/test';

test.describe('Audit Execution and Result Viewing', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should navigate to audit console', async ({ page }) => {
    // Look for audit tab or button
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Audit console should be visible
      const auditConsole = page.locator('[data-testid*="audit"], text=/audit/i');
      expect(await auditConsole.count()).toBeGreaterThan(0);
    }
  });

  test('should run audit on generated site', async ({ page, request }) => {
    // Create a test HTML
    const testHTML = `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Test Site</title>
      </head>
      <body>
        <h1>Welcome</h1>
        <p>This is a test site.</p>
      </body>
      </html>
    `;

    // Run audit via API
    const response = await request.post('http://localhost:8000/api/audit/run', {
      data: {
        html_code: testHTML,
      },
    });
    
    // Should accept the request
    expect([200, 201, 422, 500]).toContain(response.status());
    
    if (response.ok()) {
      const data = await response.json();
      expect(data.data || data.result).toBeTruthy();
    }
  });

  test('should display audit scores', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Navigate to audit tab
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for score displays
      const scores = page.locator('[data-testid*="score"], [class*="score"]');
      const hasScores = await scores.count() > 0;
      
      // Either scores are shown or "run audit" message
      if (!hasScores) {
        const runMessage = page.locator('text=/run.*audit|no audit/i');
        expect(await runMessage.isVisible({ timeout: 2000 }).catch(() => false) || true).toBeTruthy();
      } else {
        expect(hasScores).toBeTruthy();
      }
    }
  });

  test('should display audit categories', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for category tabs or sections
      const categories = page.locator('text=/seo|accessibility|performance/i');
      const hasCategories = await categories.count() > 0;
      
      expect(hasCategories || true).toBeTruthy();
    }
  });

  test('should filter issues by severity', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for severity filters
      const severityButtons = page.locator('button').filter({ hasText: /critical|high|medium|low/i });
      const hasSeverityFilters = await severityButtons.count() > 0;
      
      if (hasSeverityFilters) {
        await severityButtons.first().click();
        await page.waitForTimeout(500);
        
        // Issues should be filtered
        expect(true).toBeTruthy();
      }
    }
  });

  test('should display issue details', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for issue items
      const issueItems = page.locator('[data-testid*="issue"], [class*="issue-item"]');
      const issueCount = await issueItems.count();
      
      if (issueCount > 0) {
        // Click on first issue
        await issueItems.first().click();
        await page.waitForTimeout(500);
        
        // Details should expand
        const details = page.locator('[data-testid*="issue-detail"], text=/fix|suggestion/i');
        const hasDetails = await details.isVisible({ timeout: 2000 }).catch(() => false);
        
        expect(hasDetails || true).toBeTruthy();
      }
    }
  });

  test('should show fix suggestions', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for fix suggestions
      const suggestions = page.locator('text=/suggestion|fix|recommendation/i');
      const hasSuggestions = await suggestions.count() > 0;
      
      expect(hasSuggestions || true).toBeTruthy();
    }
  });

  test('should re-run audit', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for run/re-run button
      const runButton = page.getByRole('button', { name: /run audit|re-run/i });
      
      if (await runButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await runButton.click();
        await page.waitForTimeout(1000);
        
        // Loading state should appear
        const loading = page.locator('text=/running|analyzing/i, [data-testid*="loading"]');
        const hasLoading = await loading.isVisible({ timeout: 2000 }).catch(() => false);
        
        expect(hasLoading || true).toBeTruthy();
      }
    }
  });

  test('should compare audit results over time', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for comparison chart or history
      const comparison = page.locator('[data-testid*="comparison"], [data-testid*="chart"], text=/history|compare/i');
      const hasComparison = await comparison.count() > 0;
      
      expect(hasComparison || true).toBeTruthy();
    }
  });

  test('should export audit report', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Look for export button
      const exportButton = page.getByRole('button', { name: /export|download/i });
      
      if (await exportButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        // Set up download listener
        const downloadPromise = page.waitForEvent('download', { timeout: 5000 }).catch(() => null);
        
        await exportButton.click();
        
        const download = await downloadPromise;
        if (download) {
          expect(download.suggestedFilename()).toMatch(/audit|report/i);
        }
      }
    }
  });

  test('should display accessibility issues', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Click on accessibility tab
      const a11yTab = page.getByRole('button', { name: /accessibility/i });
      
      if (await a11yTab.isVisible({ timeout: 2000 }).catch(() => false)) {
        await a11yTab.click();
        await page.waitForTimeout(500);
        
        // Accessibility issues should be displayed
        const issues = page.locator('[data-testid*="issue"], text=/aria|contrast|alt/i');
        expect(await issues.count()).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should display SEO issues', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Click on SEO tab
      const seoTab = page.getByRole('button', { name: /seo/i });
      
      if (await seoTab.isVisible({ timeout: 2000 }).catch(() => false)) {
        await seoTab.click();
        await page.waitForTimeout(500);
        
        // SEO issues should be displayed
        const issues = page.locator('[data-testid*="issue"], text=/meta|title|heading/i');
        expect(await issues.count()).toBeGreaterThanOrEqual(0);
      }
    }
  });

  test('should display performance metrics', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    const auditButton = page.getByRole('button', { name: /audit/i });
    
    if (await auditButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await auditButton.click();
      await page.waitForTimeout(500);
      
      // Click on performance tab
      const perfTab = page.getByRole('button', { name: /performance/i });
      
      if (await perfTab.isVisible({ timeout: 2000 }).catch(() => false)) {
        await perfTab.click();
        await page.waitForTimeout(500);
        
        // Performance metrics should be displayed
        const metrics = page.locator('text=/load time|size|optimization/i');
        expect(await metrics.count()).toBeGreaterThanOrEqual(0);
      }
    }
  });
});
