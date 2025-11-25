import { Issue } from '@/lib/types/audit';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Separator } from '@/components/ui/separator';
import { Lightbulb, Code } from 'lucide-react';
import { cn } from '@/lib/utils';

interface IssueDetailProps {
  issue: Issue;
  className?: string;
}

export function IssueDetail({ issue, className }: IssueDetailProps) {
  return (
    <div className={cn('space-y-4', className)}>
      <Separator />

      {/* Fix suggestion */}
      {issue.fix_suggestion && (
        <Alert>
          <Lightbulb className="h-4 w-4" />
          <AlertDescription>
            <div className="font-semibold mb-1">Suggested Fix:</div>
            <p className="text-sm">{issue.fix_suggestion}</p>
          </AlertDescription>
        </Alert>
      )}

      {/* Affected elements */}
      {issue.affected_elements && issue.affected_elements.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Code className="h-4 w-4 text-muted-foreground" />
            <span className="text-sm font-semibold">Affected Elements:</span>
          </div>
          <div className="bg-muted rounded-md p-3 space-y-1">
            {issue.affected_elements.map((element, index) => (
              <code
                key={index}
                className="block text-xs font-mono text-muted-foreground"
              >
                {element}
              </code>
            ))}
          </div>
        </div>
      )}

      {/* Additional info if no fix suggestion or affected elements */}
      {!issue.fix_suggestion && (!issue.affected_elements || issue.affected_elements.length === 0) && (
        <p className="text-sm text-muted-foreground">
          No additional details available for this issue.
        </p>
      )}
    </div>
  );
}
