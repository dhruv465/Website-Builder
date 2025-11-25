import { useState } from 'react';
import { AuditConsole } from '@/components/audit';
import { Audit } from '@/lib/types/audit';

// Mock audit data for testing
const mockAudit: Audit = {
  id: 'audit-1',
  site_id: 'site-1',
  timestamp: new Date().toISOString(),
  overall_score: 78,
  seo: {
    score: 85,
    passed_checks: 17,
    total_checks: 20,
    issues: [
      {
        severity: 'high',
        description: 'Missing meta description tag',
        fix_suggestion: 'Add a meta description tag to your HTML head section with a concise summary of your page content (150-160 characters).',
        affected_elements: ['<head>'],
      },
      {
        severity: 'medium',
        description: 'Image alt attributes are missing',
        fix_suggestion: 'Add descriptive alt text to all images for better SEO and accessibility.',
        affected_elements: ['<img src="hero.jpg">', '<img src="logo.png">'],
      },
      {
        severity: 'low',
        description: 'H1 tag is not optimized',
        fix_suggestion: 'Ensure your H1 tag contains relevant keywords and accurately describes the page content.',
      },
    ],
  },
  accessibility: {
    score: 72,
    passed_checks: 18,
    total_checks: 25,
    issues: [
      {
        severity: 'critical',
        description: 'Form inputs missing labels',
        fix_suggestion: 'Add <label> elements associated with each form input using the "for" attribute.',
        affected_elements: ['<input type="email">', '<input type="password">'],
      },
      {
        severity: 'high',
        description: 'Insufficient color contrast',
        fix_suggestion: 'Increase the contrast ratio between text and background to at least 4.5:1 for normal text.',
        affected_elements: ['.text-gray-400', '.btn-secondary'],
      },
      {
        severity: 'medium',
        description: 'Missing ARIA landmarks',
        fix_suggestion: 'Add ARIA landmark roles (navigation, main, complementary) to improve screen reader navigation.',
      },
      {
        severity: 'low',
        description: 'Link text is not descriptive',
        fix_suggestion: 'Replace generic link text like "click here" with descriptive text that explains the link destination.',
        affected_elements: ['<a href="/about">click here</a>'],
      },
    ],
  },
  performance: {
    score: 76,
    passed_checks: 12,
    total_checks: 15,
    issues: [
      {
        severity: 'high',
        description: 'Large images not optimized',
        fix_suggestion: 'Compress images and use modern formats like WebP. Consider lazy loading for below-the-fold images.',
        affected_elements: ['hero.jpg (2.4MB)', 'banner.png (1.8MB)'],
      },
      {
        severity: 'medium',
        description: 'Render-blocking resources',
        fix_suggestion: 'Defer non-critical CSS and JavaScript to improve initial page load time.',
      },
    ],
  },
};

const mockPreviousAudits: Audit[] = [
  {
    id: 'audit-0',
    site_id: 'site-1',
    timestamp: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    overall_score: 65,
    seo: { score: 70, passed_checks: 14, total_checks: 20, issues: [] },
    accessibility: { score: 60, passed_checks: 15, total_checks: 25, issues: [] },
    performance: { score: 65, passed_checks: 10, total_checks: 15, issues: [] },
  },
  {
    id: 'audit-2',
    site_id: 'site-1',
    timestamp: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
    overall_score: 72,
    seo: { score: 78, passed_checks: 16, total_checks: 20, issues: [] },
    accessibility: { score: 68, passed_checks: 17, total_checks: 25, issues: [] },
    performance: { score: 70, passed_checks: 11, total_checks: 15, issues: [] },
  },
];

export function AuditTestPage() {
  const [audit, setAudit] = useState<Audit>(mockAudit);

  const handleRerun = async () => {
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    // Update with slightly improved scores
    setAudit({
      ...audit,
      timestamp: new Date().toISOString(),
      overall_score: Math.min(100, audit.overall_score + Math.random() * 5),
      seo: {
        ...audit.seo,
        score: Math.min(100, audit.seo.score + Math.random() * 5),
      },
      accessibility: {
        ...audit.accessibility,
        score: Math.min(100, audit.accessibility.score + Math.random() * 5),
      },
      performance: {
        ...audit.performance,
        score: Math.min(100, audit.performance.score + Math.random() * 5),
      },
    });
  };

  const handleExport = (format: 'json' | 'pdf') => {
    if (format === 'json') {
      const dataStr = JSON.stringify(audit, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `audit-${audit.id}.json`;
      link.click();
      URL.revokeObjectURL(url);
    } else {
      // PDF export would require a library like jsPDF
      alert('PDF export functionality would be implemented with a library like jsPDF');
    }
  };

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Audit Console Test</h1>
        <p className="text-muted-foreground">
          Testing the AuditConsole component with mock data
        </p>
      </div>

      <AuditConsole
        audit={audit}
        previousAudits={mockPreviousAudits}
        onRerun={handleRerun}
        onExport={handleExport}
      />
    </div>
  );
}
