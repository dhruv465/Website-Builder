import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AuditConsole } from './AuditConsole';
import { Audit } from '@/lib/types/audit';

// Mock child components
vi.mock('./ScoreCard', () => ({
  ScoreCard: ({ title, score }: any) => (
    <div data-testid={`score-card-${title.toLowerCase()}`}>
      {title}: {score}
    </div>
  ),
}));

vi.mock('./IssueList', () => ({
  IssueList: ({ issues }: any) => (
    <div data-testid="issue-list">
      {issues.map((issue: any, idx: number) => (
        <div key={idx}>{issue.description}</div>
      ))}
    </div>
  ),
}));

vi.mock('./ComparisonChart', () => ({
  ComparisonChart: () => <div data-testid="comparison-chart">Chart</div>,
}));

vi.mock('./RecommendationPanel', () => ({
  RecommendationPanel: () => <div data-testid="recommendation-panel">Recommendations</div>,
}));

describe('AuditConsole', () => {
  const mockAudit: Audit = {
    id: 'audit-1',
    site_id: 'site-1',
    timestamp: '2024-01-01T12:00:00Z',
    seo: {
      score: 85,
      passed_checks: 8,
      total_checks: 10,
      issues: [
        {
          severity: 'medium',
          description: 'Missing meta description',
          fix_suggestion: 'Add meta description tag',
        },
      ],
    },
    accessibility: {
      score: 92,
      passed_checks: 9,
      total_checks: 10,
      issues: [
        {
          severity: 'low',
          description: 'Image missing alt text',
          fix_suggestion: 'Add alt attribute to images',
        },
      ],
    },
    performance: {
      score: 78,
      passed_checks: 7,
      total_checks: 10,
      issues: [
        {
          severity: 'high',
          description: 'Large image files',
          fix_suggestion: 'Optimize and compress images',
        },
      ],
    },
    overall_score: 85,
  };

  const mockOnRerun = vi.fn();
  const mockOnExport = vi.fn();

  beforeEach(() => {
    mockOnRerun.mockClear();
    mockOnExport.mockClear();
  });

  it('renders audit console with header', () => {
    render(<AuditConsole audit={mockAudit} />);

    expect(screen.getByText('Audit Results')).toBeInTheDocument();
    expect(screen.getByText(/Last run:/i)).toBeInTheDocument();
  });

  it('displays score cards for all categories', () => {
    render(<AuditConsole audit={mockAudit} />);

    expect(screen.getByTestId('score-card-seo')).toBeInTheDocument();
    expect(screen.getByTestId('score-card-accessibility')).toBeInTheDocument();
    expect(screen.getByTestId('score-card-performance')).toBeInTheDocument();
  });

  it('displays overall score', () => {
    render(<AuditConsole audit={mockAudit} />);

    expect(screen.getByText('Overall Score')).toBeInTheDocument();
    expect(screen.getByText('85')).toBeInTheDocument();
  });

  it('renders tabs for different categories', () => {
    render(<AuditConsole audit={mockAudit} />);

    expect(screen.getByRole('tab', { name: /overview/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /seo/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /accessibility/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /performance/i })).toBeInTheDocument();
  });

  it('shows issue count badges on tabs', () => {
    render(<AuditConsole audit={mockAudit} />);

    const seoTab = screen.getByRole('tab', { name: /seo/i });
    expect(seoTab).toHaveTextContent('1');
  });

  it('calls onRerun when re-run button is clicked', async () => {
    const user = userEvent.setup();
    mockOnRerun.mockResolvedValue(undefined);

    render(<AuditConsole audit={mockAudit} onRerun={mockOnRerun} />);

    const rerunButton = screen.getByRole('button', { name: /re-run audit/i });
    await user.click(rerunButton);

    await waitFor(() => {
      expect(mockOnRerun).toHaveBeenCalledTimes(1);
    });
  });

  it('shows loading state during re-run', async () => {
    const user = userEvent.setup();
    mockOnRerun.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

    render(<AuditConsole audit={mockAudit} onRerun={mockOnRerun} />);

    const rerunButton = screen.getByRole('button', { name: /re-run audit/i });
    await user.click(rerunButton);

    expect(screen.getByText(/running/i)).toBeInTheDocument();
  });

  it('opens export dropdown and calls onExport', async () => {
    const user = userEvent.setup();

    render(<AuditConsole audit={mockAudit} onExport={mockOnExport} />);

    const exportButton = screen.getByRole('button', { name: /export/i });
    await user.click(exportButton);

    const jsonOption = screen.getByText(/export as json/i);
    await user.click(jsonOption);

    expect(mockOnExport).toHaveBeenCalledWith('json');
  });

  it('switches between tabs', async () => {
    const user = userEvent.setup();
    render(<AuditConsole audit={mockAudit} />);

    const seoTab = screen.getByRole('tab', { name: /seo/i });
    await user.click(seoTab);

    expect(screen.getByText('SEO Issues')).toBeInTheDocument();
  });

  it('displays comparison chart when previous audits exist', () => {
    const previousAudits = [
      { ...mockAudit, id: 'audit-0', timestamp: '2024-01-01T11:00:00Z' },
    ];

    render(<AuditConsole audit={mockAudit} previousAudits={previousAudits} />);

    expect(screen.getByTestId('comparison-chart')).toBeInTheDocument();
  });

  it('formats timestamp correctly', () => {
    render(<AuditConsole audit={mockAudit} />);

    expect(screen.getByText(/Jan 1, 2024/i)).toBeInTheDocument();
  });
});
