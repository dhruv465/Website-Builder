import { test, expect } from '@playwright/test';
import { injectAxe, checkA11y } from 'axe-playwright';

test.describe('Accessibility Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
    await injectAxe(page);
  });

  test('Homepage should have no accessibility violations', async ({ page }) => {
    await checkA11y(page, null, {
      detailedReport: true,
      detailedReportOptions: {
        html: true,
      },
    });
  });

  test('Builder page should have no accessibility violations', async ({ page }) => {
    await page.goto('http://localhost:3000/builder');
    await checkA11y(page, null, {
      detailedReport: true,
    });
  });

  test('Dashboard should have no accessibility violations', async ({ page }) => {
    await page.goto('http://localhost:3000/dashboard');
    await checkA11y(page, null, {
      detailedReport: true,
    });
  });

  test('Should have proper heading hierarchy', async ({ page }) => {
    const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
    expect(headings.length).toBeGreaterThan(0);
    
    // Check that h1 exists
    const h1Count = await page.locator('h1').count();
    expect(h1Count).toBeGreaterThanOrEqual(1);
  });

  test('All images should have alt text', async ({ page }) => {
    const images = await page.locator('img').all();
    
    for (const img of images) {
      const alt = await img.getAttribute('alt');
      expect(alt).toBeTruthy();
    }
  });

  test('All buttons should have accessible names', async ({ page }) => {
    const buttons = await page.locator('button').all();
    
    for (const button of buttons) {
      const ariaLabel = await button.getAttribute('aria-label');
      const text = await button.textContent();
      const title = await button.getAttribute('title');
      
      // Button should have either text content, aria-label, or title
      expect(ariaLabel || text?.trim() || title).toBeTruthy();
    }
  });

  test('Form inputs should have labels', async ({ page }) => {
    const inputs = await page.locator('input[type="text"], input[type="email"], textarea').all();
    
    for (const input of inputs) {
      const id = await input.getAttribute('id');
      const ariaLabel = await input.getAttribute('aria-label');
      const ariaLabelledBy = await input.getAttribute('aria-labelledby');
      const placeholder = await input.getAttribute('placeholder');
      
      // Input should have id with associated label, aria-label, or aria-labelledby
      if (id) {
        const label = await page.locator(`label[for="${id}"]`).count();
        expect(label || ariaLabel || ariaLabelledBy || placeholder).toBeTruthy();
      } else {
        expect(ariaLabel || ariaLabelledBy || placeholder).toBeTruthy();
      }
    }
  });

  test('Should support keyboard navigation', async ({ page }) => {
    // Tab through interactive elements
    await page.keyboard.press('Tab');
    const firstFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(['BUTTON', 'A', 'INPUT']).toContain(firstFocused);
    
    // Continue tabbing
    await page.keyboard.press('Tab');
    const secondFocused = await page.evaluate(() => document.activeElement?.tagName);
    expect(['BUTTON', 'A', 'INPUT']).toContain(secondFocused);
  });

  test('Should have sufficient color contrast', async ({ page }) => {
    await checkA11y(page, null, {
      rules: {
        'color-contrast': { enabled: true },
      },
    });
  });

  test('Should have proper ARIA roles', async ({ page }) => {
    await checkA11y(page, null, {
      rules: {
        'aria-roles': { enabled: true },
        'aria-allowed-attr': { enabled: true },
        'aria-required-attr': { enabled: true },
      },
    });
  });
});
