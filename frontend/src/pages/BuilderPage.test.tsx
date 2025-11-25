import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import BuilderPage from './BuilderPage';
import { SessionProvider } from '../lib/context/SessionContext';
import { WorkflowProvider } from '../lib/context/WorkflowContext';
import { ThemeProvider } from '../components/theme-provider';

// Mock API calls
vi.mock('../lib/api/sessions', () => ({
  createSession: vi.fn(() =>
    Promise.resolve({
      id: 'test-session-id',
      created_at: new Date().toISOString(),
      last_accessed_at: new Date().toISOString(),
      preferences: {},
      sites: [],
    })
  ),
  getSession: vi.fn(),
  updateSession: vi.fn(),
  updateSessionPreferences: vi.fn(),
}));

vi.mock('../lib/api/workflows', () => ({
  createWorkflow: vi.fn(),
  updateWorkflow: vi.fn(),
  cancelWorkflow: vi.fn(),
  getWorkflowStatus: vi.fn(),
}));

vi.mock('../lib/api/code', () => ({
  generateCode: vi.fn(),
  updateCode: vi.fn(),
  getSiteCode: vi.fn(),
}));

const renderBuilderPage = (_siteId?: string) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <SessionProvider>
          <WorkflowProvider>
            <BuilderPage />
          </WorkflowProvider>
        </SessionProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('BuilderPage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders builder page with main sections', async () => {
    renderBuilderPage();

    await waitFor(() => {
      expect(screen.getByText('New Website')).toBeInTheDocument();
    });

    // Check for main UI elements
    expect(screen.getByText('Back to Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Save')).toBeInTheDocument();
    expect(screen.getByText('Publish')).toBeInTheDocument();
  });

  it('displays builder form', async () => {
    renderBuilderPage();

    await waitFor(() => {
      expect(screen.getByText('Describe Your Website')).toBeInTheDocument();
    });

    expect(screen.getByLabelText('Website Requirements')).toBeInTheDocument();
  });

  it('shows preview and code mode toggle', async () => {
    renderBuilderPage();

    await waitFor(() => {
      expect(screen.getByText('Preview')).toBeInTheDocument();
    });

    expect(screen.getByText('Code')).toBeInTheDocument();
  });
});
