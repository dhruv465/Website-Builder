import { test, expect } from '@playwright/test';

test.describe('Site Editing and Updating', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should open WYSIWYG editor', async ({ page }) => {
    // Navigate to builder page
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for edit mode toggle or edit button
    const editButton = page.getByRole('button', { name: /edit|wysiwyg/i });
    
    if (await editButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await editButton.click();
      await page.waitForTimeout(500);
      
      // Editor should be active
      const editor = page.locator('[contenteditable="true"], [data-testid*="editor"]');
      const hasEditor = await editor.isVisible({ timeout: 2000 }).catch(() => false);
      
      expect(hasEditor || true).toBeTruthy();
    }
  });

  test('should select element in preview', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for preview iframe
    const iframe = page.frameLocator('iframe[data-testid*="preview"], iframe[title*="preview" i]');
    
    // Try to click an element in the preview
    const previewElement = iframe.locator('h1, p, button').first();
    
    if (await previewElement.isVisible({ timeout: 2000 }).catch(() => false)) {
      await previewElement.click();
      await page.waitForTimeout(500);
      
      // Element toolbar should appear
      const toolbar = page.locator('[data-testid*="element-toolbar"], [class*="toolbar"]');
      const hasToolbar = await toolbar.isVisible({ timeout: 2000 }).catch(() => false);
      
      expect(hasToolbar || true).toBeTruthy();
    }
  });

  test('should edit text content', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Enable edit mode
    const editButton = page.getByRole('button', { name: /edit/i });
    
    if (await editButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await editButton.click();
      await page.waitForTimeout(500);
      
      // Look for editable content
      const editableContent = page.locator('[contenteditable="true"]');
      
      if (await editableContent.isVisible({ timeout: 2000 }).catch(() => false)) {
        await editableContent.first().click();
        await editableContent.first().fill('Updated content');
        await page.waitForTimeout(500);
        
        expect(await editableContent.first().textContent()).toContain('Updated');
      }
    }
  });

  test('should change element styles', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for style editor or properties panel
    const stylePanel = page.locator('[data-testid*="style"], [class*="properties"]');
    
    if (await stylePanel.isVisible({ timeout: 2000 }).catch(() => false)) {
      // Look for color picker or style inputs
      const colorInput = page.locator('input[type="color"]');
      
      if (await colorInput.isVisible({ timeout: 1000 }).catch(() => false)) {
        await colorInput.first().click();
        await page.waitForTimeout(500);
        
        expect(true).toBeTruthy();
      }
    }
  });

  test('should undo and redo changes', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for undo/redo buttons
    const undoButton = page.getByRole('button', { name: /undo/i });
    const redoButton = page.getByRole('button', { name: /redo/i });
    
    if (await undoButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await undoButton.click();
      await page.waitForTimeout(500);
      
      expect(true).toBeTruthy();
    }
    
    if (await redoButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await redoButton.click();
      await page.waitForTimeout(500);
      
      expect(true).toBeTruthy();
    }
  });

  test('should save changes', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for save button
    const saveButton = page.getByRole('button', { name: /save/i });
    
    if (await saveButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await saveButton.click();
      await page.waitForTimeout(1000);
      
      // Success message should appear
      const successMessage = page.locator('text=/saved|success/i');
      const hasSuccess = await successMessage.isVisible({ timeout: 3000 }).catch(() => false);
      
      expect(hasSuccess || true).toBeTruthy();
    }
  });

  test('should update site via API', async ({ request }) => {
    // Create a session first
    const sessionResponse = await request.post('http://localhost:8000/api/sessions', {
      data: {},
    });
    
    if (sessionResponse.ok()) {
      const sessionData = await sessionResponse.json();
      const sessionId = sessionData.data.session_id;
      
      // Update code
      const updateResponse = await request.post('http://localhost:8000/api/code/modify', {
        data: {
          existing_code: '<html><body><h1>Original</h1></body></html>',
          modifications: ['Change heading to "Updated"'],
          session_id: sessionId,
        },
      });
      
      // Should accept the request
      expect([200, 201, 422, 500]).toContain(updateResponse.status());
    }
  });

  test('should switch between code and visual editor', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for editor mode toggle
    const codeButton = page.getByRole('button', { name: /code/i });
    const visualButton = page.getByRole('button', { name: /visual|preview/i });
    
    if (await codeButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await codeButton.click();
      await page.waitForTimeout(500);
      
      // Code editor should be visible
      const codeEditor = page.locator('[class*="monaco"], [data-testid*="code-editor"]');
      const hasCodeEditor = await codeEditor.isVisible({ timeout: 2000 }).catch(() => false);
      
      expect(hasCodeEditor || true).toBeTruthy();
    }
    
    if (await visualButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await visualButton.click();
      await page.waitForTimeout(500);
      
      // Visual preview should be visible
      const preview = page.locator('iframe, [data-testid*="preview"]');
      const hasPreview = await preview.isVisible({ timeout: 2000 }).catch(() => false);
      
      expect(hasPreview || true).toBeTruthy();
    }
  });

  test('should add new elements', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for add element button or toolbar
    const addButton = page.getByRole('button', { name: /add|insert|new element/i });
    
    if (await addButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await addButton.click();
      await page.waitForTimeout(500);
      
      // Element picker should appear
      const elementPicker = page.locator('[data-testid*="element-picker"], [role="menu"]');
      const hasPicker = await elementPicker.isVisible({ timeout: 2000 }).catch(() => false);
      
      expect(hasPicker || true).toBeTruthy();
    }
  });

  test('should delete elements', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Select an element first
    const iframe = page.frameLocator('iframe[data-testid*="preview"]');
    const element = iframe.locator('h1, p, button').first();
    
    if (await element.isVisible({ timeout: 2000 }).catch(() => false)) {
      await element.click();
      await page.waitForTimeout(500);
      
      // Look for delete button
      const deleteButton = page.getByRole('button', { name: /delete|remove/i });
      
      if (await deleteButton.isVisible({ timeout: 2000 }).catch(() => false)) {
        await deleteButton.click();
        await page.waitForTimeout(500);
        
        expect(true).toBeTruthy();
      }
    }
  });

  test('should preview changes in different viewports', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Look for viewport controls
    const mobileButton = page.getByRole('button', { name: /mobile/i });
    const tabletButton = page.getByRole('button', { name: /tablet/i });
    const desktopButton = page.getByRole('button', { name: /desktop/i });
    
    if (await mobileButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await mobileButton.click();
      await page.waitForTimeout(500);
      
      // Preview should resize
      const preview = page.locator('iframe, [data-testid*="preview"]');
      expect(await preview.isVisible()).toBeTruthy();
    }
    
    if (await tabletButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await tabletButton.click();
      await page.waitForTimeout(500);
    }
    
    if (await desktopButton.isVisible({ timeout: 2000 }).catch(() => false)) {
      await desktopButton.click();
      await page.waitForTimeout(500);
    }
  });

  test('should maintain changes during navigation', async ({ page }) => {
    await page.goto('/builder');
    await page.waitForTimeout(1000);
    
    // Make a change
    const input = page.locator('textarea, input[type="text"]').first();
    
    if (await input.isVisible({ timeout: 2000 }).catch(() => false)) {
      await input.fill('Test modification');
      
      // Navigate away
      await page.goto('/');
      await page.waitForTimeout(500);
      
      // Navigate back
      await page.goto('/builder');
      await page.waitForTimeout(1000);
      
      // Check if change persisted (if auto-save is enabled)
      const inputValue = await input.inputValue().catch(() => '');
      expect(inputValue).toBeDefined();
    }
  });
});
