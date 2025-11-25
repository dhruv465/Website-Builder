import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Audit } from '@/lib/types/audit';
import { ScoreCard } from './ScoreCard';
import { IssueList } from './IssueList';
import { ComparisonChart } from './ComparisonChart';
import { RecommendationPanel } from './RecommendationPanel';
import { RefreshCw, Download, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface AuditConsoleProps {
  audit: Audit;
  previousAudits?: Audit[];
  onRerun?: () => Promise<void>;
  onExport?: (format: 'json' | 'pdf') => void;
  className?: string;
}

export function AuditConsole({
  audit,
  previousAudits = [],
  onRerun,
  onExport,
  className,
}: AuditConsoleProps) {
  const [isRerunning, setIsRerunning] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const handleRerun = async () => {
    if (!onRerun) return;
    
    setIsRerunning(true);
    try {
      await onRerun();
    } catch (error) {
      console.error('Failed to rerun audit:', error);
    } finally {
      setIsRerunning(false);
    }
  };

  const handleExport = (format: 'json' | 'pdf') => {
    if (onExport) {
      onExport(format);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header with actions */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Audit Results</CardTitle>
              <p className="text-sm text-muted-foreground mt-1">
                Last run: {formatTimestamp(audit.timestamp)}
              </p>
            </div>
            <div className="flex gap-2">
              {onRerun && (
                <Button
                  onClick={handleRerun}
                  disabled={isRerunning}
                  variant="outline"
                >
                  {isRerunning ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <RefreshCw className="mr-2 h-4 w-4" />
                      Re-run Audit
                    </>
                  )}
                </Button>
              )}
              {onExport && (
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="outline">
                      <Download className="mr-2 h-4 w-4" />
                      Export
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent>
                    <DropdownMenuItem onClick={() => handleExport('json')}>
                      Export as JSON
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => handleExport('pdf')}>
                      Export as PDF
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              )}
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Overall Score Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ScoreCard
          title="SEO"
          score={audit.seo.score}
          passedChecks={audit.seo.passed_checks}
          totalChecks={audit.seo.total_checks}
        />
        <ScoreCard
          title="Accessibility"
          score={audit.accessibility.score}
          passedChecks={audit.accessibility.passed_checks}
          totalChecks={audit.accessibility.total_checks}
        />
        <ScoreCard
          title="Performance"
          score={audit.performance.score}
          passedChecks={audit.performance.passed_checks}
          totalChecks={audit.performance.total_checks}
        />
      </div>

      {/* Overall Score */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold">Overall Score</h3>
              <p className="text-sm text-muted-foreground">
                Combined score across all categories
              </p>
            </div>
            <div className="text-4xl font-bold">
              {Math.round(audit.overall_score)}
              <span className="text-xl text-muted-foreground">/100</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs for detailed view */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="seo">
            SEO
            {audit.seo.issues.length > 0 && (
              <span className="ml-2 text-xs bg-destructive text-destructive-foreground rounded-full px-2 py-0.5">
                {audit.seo.issues.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="accessibility">
            Accessibility
            {audit.accessibility.issues.length > 0 && (
              <span className="ml-2 text-xs bg-destructive text-destructive-foreground rounded-full px-2 py-0.5">
                {audit.accessibility.issues.length}
              </span>
            )}
          </TabsTrigger>
          <TabsTrigger value="performance">
            Performance
            {audit.performance.issues.length > 0 && (
              <span className="ml-2 text-xs bg-destructive text-destructive-foreground rounded-full px-2 py-0.5">
                {audit.performance.issues.length}
              </span>
            )}
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <RecommendationPanel audit={audit} />
          {previousAudits.length > 0 && (
            <ComparisonChart audits={[...previousAudits, audit]} />
          )}
        </TabsContent>

        <TabsContent value="seo">
          <Card>
            <CardHeader>
              <CardTitle>SEO Issues</CardTitle>
            </CardHeader>
            <CardContent>
              <IssueList issues={audit.seo.issues} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="accessibility">
          <Card>
            <CardHeader>
              <CardTitle>Accessibility Issues</CardTitle>
            </CardHeader>
            <CardContent>
              <IssueList issues={audit.accessibility.issues} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="performance">
          <Card>
            <CardHeader>
              <CardTitle>Performance Issues</CardTitle>
            </CardHeader>
            <CardContent>
              <IssueList issues={audit.performance.issues} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
