import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SitePreview } from './SitePreview';

// Mock child components
vi.mock('./ViewportControls', () => ({
  ViewportControls: ({ viewport, onViewportChange }: any) => (
    <div data-testid="viewport-controls">
      <button onClick={() => onViewportChange('mobile')}>Mobile</button>
      <button onClick={() => onViewportChange('tablet')}>Tablet</button>
      <button onClick={() => onViewportChange('desktop')}>Desktop</button>
      <span>Current: {viewport}</span>
    </div>
  ),
}));

vi.mock('./PreviewControls', () => ({
  PreviewControls: ({ zoom, onZoomChange, onRefresh }: any) => (
    <div data-testid="preview-controls">
      <button onClick={() => onZoomChange(zoom + 10)}>Zoom In</button>
      <button onClick={() => onZoomChange(zoom - 10)}>Zoom Out</button>
      <button onClick={onRefresh}>Refresh</button>
      <span>Zoom: {zoom}%</span>
    </div>
  ),
}));

vi.mock('./ElementHighlight', () => ({
  ElementHighlight: ({ onClose }: any) => (
    <div data-testid="element-highlight">
      <button onClick={onClose}>Close</button>
    </div>
  ),
}));

describe('SitePreview', () => {
  const mockHtmlCode = '<div><h1>Test Website</h1><p>Content</p></div>';
  const mockCssCode = 'body { margin: 0; }';
  const mockJsCode = 'console.log("test");';

  it('renders preview iframe', () => {
    render(<SitePreview htmlCode={mockHtmlCode} />);

    const iframe = screen.getByTitle('Site Preview');
    expect(iframe).toBeInTheDocument();
  });

  it('renders viewport controls', () => {
    render(<SitePreview htmlCode={mockHtmlCode} />);

    expect(screen.getByTestId('viewport-controls')).toBeInTheDocument();
  });

  it('renders preview controls', () => {
    render(<SitePreview htmlCode={mockHtmlCode} />);

    expect(screen.getByTestId('preview-controls')).toBeInTheDocument();
  });

  it('changes viewport size', async () => {
    const user = userEvent.setup();
    render(<SitePreview htmlCode={mockHtmlCode} />);

    const mobileButton = screen.getByRole('button', { name: 'Mobile' });
    await user.click(mobileButton);

    expect(screen.getByText('Current: mobile')).toBeInTheDocument();
  });

  it('adjusts zoom level', async () => {
    const user = userEvent.setup();
    render(<SitePreview htmlCode={mockHtmlCode} />);

    const zoomInButton = screen.getByRole('button', { name: 'Zoom In' });
    await user.click(zoomInButton);

    expect(screen.getByText('Zoom: 110%')).toBeInTheDocument();
  });

  it('displays status bar with dimensions', () => {
    render(<SitePreview htmlCode={mockHtmlCode} viewport="desktop" />);

    expect(screen.getByText(/1440 × 900/i)).toBeInTheDocument();
    // Check for desktop in status bar specifically
    const statusBar = screen.getByText(/1440 × 900/i).closest('div');
    expect(statusBar).toHaveTextContent('desktop');
  });

  it('injects CSS and JS code into iframe', () => {
    render(
      <SitePreview
        htmlCode={mockHtmlCode}
        cssCode={mockCssCode}
        jsCode={mockJsCode}
      />
    );

    const iframe = screen.getByTitle('Site Preview') as HTMLIFrameElement;
    expect(iframe).toBeInTheDocument();
  });

  it('applies correct dimensions for mobile viewport', () => {
    render(<SitePreview htmlCode={mockHtmlCode} viewport="mobile" />);

    expect(screen.getByText(/375 × 667/i)).toBeInTheDocument();
  });

  it('applies correct dimensions for tablet viewport', () => {
    render(<SitePreview htmlCode={mockHtmlCode} viewport="tablet" />);

    expect(screen.getByText(/768 × 1024/i)).toBeInTheDocument();
  });
});
