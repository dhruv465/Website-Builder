# Audit Components

This directory contains components for displaying and managing website audit results.

## Components

### AuditConsole

The main component that orchestrates all audit-related functionality.

**Features:**
- Category tabs (Overview, SEO, Accessibility, Performance)
- Score visualization with circular progress indicators
- Issue filtering and search
- Historical score comparison charts
- Audit re-run functionality
- Export to JSON/PDF

**Usage:**
```tsx
import { AuditConsole } from '@/components/audit';

<AuditConsole
  audit={currentAudit}
  previousAudits={historicalAudits}
  onRerun={handleRerun}
  onExport={handleExport}
/>
```

### ScoreCard

Displays a category score with a circular progress indicator.

**Props:**
- `title`: Category name (e.g., "SEO", "Accessibility")
- `score`: Score value (0-100)
- `passedChecks`: Number of checks that passed
- `totalChecks`: Total number of checks

**Color Coding:**
- Green (90-100): Excellent
- Yellow (70-89): Good
- Orange (50-69): Needs improvement
- Red (0-49): Poor

### IssueList

Displays a filterable list of issues with severity badges.

**Features:**
- Search by description
- Filter by severity (critical, high, medium, low)
- Expandable issue details
- Severity color coding

### IssueDetail

Shows detailed information about a specific issue.

**Displays:**
- Fix suggestions
- Affected HTML elements
- Additional context

### ComparisonChart

Line chart showing score trends over time using Recharts.

**Features:**
- Multiple data series (SEO, Accessibility, Performance, Overall)
- Responsive design
- Tooltip with detailed information
- Automatic date formatting

### RecommendationPanel

Generates actionable recommendations based on audit results.

**Features:**
- Priority-based recommendations (high, medium, low)
- Category-specific suggestions
- Impact assessment
- Positive feedback for good scores

## Data Types

```typescript
interface Audit {
  id: string;
  site_id: string;
  timestamp: string;
  overall_score: number;
  seo: CategoryScore;
  accessibility: CategoryScore;
  performance: CategoryScore;
}

interface CategoryScore {
  score: number;
  issues: Issue[];
  passed_checks: number;
  total_checks: number;
}

interface Issue {
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  fix_suggestion?: string;
  affected_elements?: string[];
}
```

## Testing

Visit `/dashboard/audit-test` to see the AuditConsole in action with mock data.

## Export Functionality

### JSON Export
Exports the complete audit data as a JSON file for programmatic processing.

### PDF Export
Requires integration with a PDF generation library like jsPDF or react-pdf. The handler is provided but needs implementation.

## Accessibility

All components follow WCAG 2.1 AA guidelines:
- Keyboard navigation support
- ARIA labels and roles
- Sufficient color contrast
- Screen reader compatible

## Performance

- Memoized filtering and sorting
- Lazy rendering for large issue lists
- Optimized chart rendering with Recharts
- Minimal re-renders with proper React patterns
