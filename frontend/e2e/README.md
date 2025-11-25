# End-to-End Tests

This directory contains E2E tests for the Smart Multi-Agent Website Builder using Playwright.

## Running Tests

### Prerequisites

Install Playwright browsers:
```bash
npx playwright install
```

### Run all E2E tests
```bash
npm run test:e2e
```

### Run tests in UI mode (interactive)
```bash
npm run test:e2e:ui
```

### Run tests in headed mode (see browser)
```bash
npm run test:e2e:headed
```

### Run specific test file
```bash
npx playwright test e2e/basic-workflow.spec.ts
```

### Run tests on specific browser
```bash
npx playwright test --project=chromium
npx playwright test --project=firefox
npx playwright test --project=webkit
```

## Test Structure

- `basic-workflow.spec.ts` - Tests basic application functionality and navigation
- `complete-workflow.spec.ts` - Tests complete site creation workflow from start to finish
- `site-editing.spec.ts` - Tests site editing and updating functionality
- `audit-workflow.spec.ts` - Tests audit execution and result viewing
- `theme-selection.spec.ts` - Tests theme selection and application
- `project-history.spec.ts` - Tests project history and version management
- `deployment-workflow.spec.ts` - Tests deployment workflow and status tracking
- `session-persistence.spec.ts` - Tests session state management and persistence
- `responsive-design.spec.ts` - Tests responsive behavior across different screen sizes
- `error-handling.spec.ts` - Tests error scenarios and recovery
- `accessibility.spec.ts` - Tests accessibility features with axe-core integration
- `integration-workflow.spec.ts` - Tests frontend-backend integration

## Test Coverage

The E2E tests cover:

1. **Complete Site Creation**: Full workflow from requirements input to site generation
2. **Site Editing**: WYSIWYG editing, element selection, style changes, undo/redo
3. **Audit Workflow**: Running audits, viewing results, filtering issues, exporting reports
4. **Theme Management**: Browsing themes, previewing, applying, customizing colors
5. **Project History**: Viewing projects, version history, restoring versions, duplicating/deleting
6. **Deployment**: Configuring deployment, monitoring progress, viewing logs, handling errors
7. **Session Persistence**: State management across page reloads and navigation
8. **Voice Input**: Voice-to-text functionality (when available)
9. **Chat Interface**: Conversational input for site requirements
10. **Responsive Design**: Testing on different device sizes and viewports
11. **Error Handling**: Graceful error handling, retry mechanisms, recovery
12. **Accessibility**: WCAG 2.1 AA compliance with axe-core automated testing
13. **Real-time Updates**: WebSocket connections and agent activity monitoring
14. **API Integration**: Frontend-backend communication and data flow

## Debugging Tests

### View test report
```bash
npx playwright show-report
```

### Debug specific test
```bash
npx playwright test --debug e2e/basic-workflow.spec.ts
```

### Generate trace
```bash
npx playwright test --trace on
```

## CI/CD Integration

Tests are configured to run in CI with:
- Automatic retries (2 retries on failure)
- Sequential execution (no parallel tests)
- HTML report generation

## Notes

- Tests require the development server to be running on `http://localhost:3000`
- The `webServer` configuration in `playwright.config.ts` automatically starts the dev server
- Tests are designed to be resilient and handle timing issues with proper waits
- Some tests may be skipped if certain features are not yet implemented
