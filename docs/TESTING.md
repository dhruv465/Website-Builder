# Testing Guide

This document outlines the testing infrastructure and procedures for the AI-Powered Website Builder.

## Frontend Testing

The frontend uses **Vitest** for unit/integration testing and **Playwright** for end-to-end testing.

### Running Unit Tests
Unit tests are located in `src/**/__tests__` directories or alongside components with `.test.tsx` extension.

```bash
cd frontend
npm test
```

To run in watch mode:
```bash
npm test -- --watch
```

To run with UI:
```bash
npm run test:ui
```

### Running E2E Tests
End-to-end tests ensure critical user flows work as expected.

```bash
cd frontend
npm run test:e2e
```

## Backend Testing

The backend uses **pytest** for unit and integration testing.

### Prerequisites
Ensure you have the virtual environment activated and dependencies installed.
You also need Redis running for Celery tests (though mocked in most cases).

### Running Tests
Run all tests from the `backend` directory:

```bash
cd backend
# Set required environment variables for testing
CELERY_BROKER_URL=redis://localhost:6379/0 CELERY_RESULT_BACKEND=redis://localhost:6379/0 PYTHONPATH=. ./venv/bin/pytest
```

### Test Structure
- `tests/test_agents.py`: Unit tests for AI agents (mocked external APIs).
- `tests/test_integration.py`: Integration tests for API endpoints.
- `tests/conftest.py`: Test fixtures (DB session, API client, mocks).

## Continuous Integration

Tests are designed to run in CI/CD pipelines. Ensure environment variables are configured in your CI provider.
