import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import App from './App';

// Mock the API calls
vi.mock('./lib/api/sessions', () => ({
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

describe('App', () => {
  it('renders the landing page by default', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/Build Websites with/i)).toBeInTheDocument();
    });
  });

  it('renders the AI-Powered Magic heading', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByText(/AI-Powered Magic/i)).toBeInTheDocument();
    });
  });

  it('renders the Get Started button', async () => {
    render(<App />);
    
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Get Started/i })).toBeInTheDocument();
    });
  });
});
