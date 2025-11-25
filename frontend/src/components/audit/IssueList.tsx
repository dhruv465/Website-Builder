import { useState, useMemo } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Issue } from '@/lib/types/audit';
import { IssueDetail } from './IssueDetail';
import { Search, Filter } from 'lucide-react';

interface IssueListProps {
  issues: Issue[];
  className?: string;
}

type SeverityFilter = 'all' | 'critical' | 'high' | 'medium' | 'low';

export function IssueList({ issues, className }: IssueListProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<SeverityFilter>('all');
  const [expandedIssueIndex, setExpandedIssueIndex] = useState<number | null>(null);

  // Filter issues based on search and severity
  const filteredIssues = useMemo(() => {
    return issues.filter((issue) => {
      const matchesSearch = issue.description
        .toLowerCase()
        .includes(searchQuery.toLowerCase());
      const matchesSeverity =
        severityFilter === 'all' || issue.severity === severityFilter;
      return matchesSearch && matchesSeverity;
    });
  }, [issues, searchQuery, severityFilter]);

  // Get severity badge variant
  const getSeverityVariant = (severity: Issue['severity']) => {
    switch (severity) {
      case 'critical':
        return 'destructive';
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
      default:
        return 'outline';
    }
  };

  // Get severity color for border
  const getSeverityBorderColor = (severity: Issue['severity']) => {
    switch (severity) {
      case 'critical':
        return 'border-l-red-600';
      case 'high':
        return 'border-l-orange-600';
      case 'medium':
        return 'border-l-yellow-600';
      case 'low':
        return 'border-l-blue-600';
      default:
        return 'border-l-gray-600';
    }
  };

  const toggleIssue = (index: number) => {
    setExpandedIssueIndex(expandedIssueIndex === index ? null : index);
  };

  return (
    <div className={className}>
      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search issues..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select
          value={severityFilter}
          onValueChange={(value) => setSeverityFilter(value as SeverityFilter)}
        >
          <SelectTrigger className="w-[180px]">
            <Filter className="h-4 w-4 mr-2" />
            <SelectValue placeholder="Filter by severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Issues list */}
      <div className="space-y-2">
        {filteredIssues.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            {issues.length === 0
              ? 'No issues found. Great job!'
              : 'No issues match your filters.'}
          </div>
        ) : (
          filteredIssues.map((issue, index) => (
            <div
              key={index}
              className={`border-l-4 ${getSeverityBorderColor(issue.severity)} bg-card rounded-lg p-4 cursor-pointer hover:bg-accent/50 transition-colors`}
              onClick={() => toggleIssue(index)}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge variant={getSeverityVariant(issue.severity)}>
                      {issue.severity.toUpperCase()}
                    </Badge>
                    {issue.affected_elements && issue.affected_elements.length > 0 && (
                      <span className="text-xs text-muted-foreground">
                        {issue.affected_elements.length} element(s) affected
                      </span>
                    )}
                  </div>
                  <p className="text-sm">{issue.description}</p>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    toggleIssue(index);
                  }}
                >
                  {expandedIssueIndex === index ? 'Hide' : 'Details'}
                </Button>
              </div>

              {/* Expanded details */}
              {expandedIssueIndex === index && (
                <IssueDetail issue={issue} className="mt-4" />
              )}
            </div>
          ))
        )}
      </div>

      {/* Summary */}
      {filteredIssues.length > 0 && (
        <div className="mt-4 text-sm text-muted-foreground">
          Showing {filteredIssues.length} of {issues.length} issue(s)
        </div>
      )}
    </div>
  );
}
