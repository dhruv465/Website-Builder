import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Audit } from '@/lib/types/audit';
import { CheckCircle2, AlertCircle, TrendingUp } from 'lucide-react';

interface RecommendationPanelProps {
  audit: Audit;
  className?: string;
}

interface Recommendation {
  priority: 'high' | 'medium' | 'low';
  category: string;
  title: string;
  description: string;
  impact: string;
}

export function RecommendationPanel({ audit, className }: RecommendationPanelProps) {
  // Generate recommendations based on audit results
  const recommendations = useMemo(() => {
    const recs: Recommendation[] = [];

    // Check SEO issues
    const criticalSeoIssues = audit.seo.issues.filter(
      (i) => i.severity === 'critical' || i.severity === 'high'
    );
    if (criticalSeoIssues.length > 0) {
      recs.push({
        priority: 'high',
        category: 'SEO',
        title: 'Fix Critical SEO Issues',
        description: `You have ${criticalSeoIssues.length} critical SEO issue(s) that need immediate attention.`,
        impact: 'High impact on search engine rankings',
      });
    } else if (audit.seo.score < 90) {
      recs.push({
        priority: 'medium',
        category: 'SEO',
        title: 'Improve SEO Score',
        description: 'Address remaining SEO issues to improve search visibility.',
        impact: 'Moderate impact on search rankings',
      });
    }

    // Check Accessibility issues
    const criticalA11yIssues = audit.accessibility.issues.filter(
      (i) => i.severity === 'critical' || i.severity === 'high'
    );
    if (criticalA11yIssues.length > 0) {
      recs.push({
        priority: 'high',
        category: 'Accessibility',
        title: 'Fix Accessibility Barriers',
        description: `${criticalA11yIssues.length} critical accessibility issue(s) may prevent users from accessing your site.`,
        impact: 'Affects users with disabilities and legal compliance',
      });
    } else if (audit.accessibility.score < 90) {
      recs.push({
        priority: 'medium',
        category: 'Accessibility',
        title: 'Enhance Accessibility',
        description: 'Improve accessibility to reach a wider audience.',
        impact: 'Better user experience for all users',
      });
    }

    // Check Performance issues
    const criticalPerfIssues = audit.performance.issues.filter(
      (i) => i.severity === 'critical' || i.severity === 'high'
    );
    if (criticalPerfIssues.length > 0) {
      recs.push({
        priority: 'high',
        category: 'Performance',
        title: 'Optimize Performance',
        description: `${criticalPerfIssues.length} performance issue(s) may be slowing down your site.`,
        impact: 'Affects user experience and conversion rates',
      });
    } else if (audit.performance.score < 90) {
      recs.push({
        priority: 'low',
        category: 'Performance',
        title: 'Fine-tune Performance',
        description: 'Minor optimizations can further improve load times.',
        impact: 'Incremental improvements to user experience',
      });
    }

    // Add positive feedback if scores are good
    if (audit.overall_score >= 90) {
      recs.push({
        priority: 'low',
        category: 'Overall',
        title: 'Excellent Work!',
        description: 'Your site meets high quality standards. Keep monitoring for any new issues.',
        impact: 'Maintain current quality levels',
      });
    }

    // Sort by priority
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    return recs.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
  }, [audit]);

  const getPriorityVariant = (priority: Recommendation['priority']) => {
    switch (priority) {
      case 'high':
        return 'destructive';
      case 'medium':
        return 'default';
      case 'low':
        return 'secondary';
    }
  };

  const getPriorityIcon = (priority: Recommendation['priority']) => {
    switch (priority) {
      case 'high':
        return <AlertCircle className="h-5 w-5 text-destructive" />;
      case 'medium':
        return <TrendingUp className="h-5 w-5 text-primary" />;
      case 'low':
        return <CheckCircle2 className="h-5 w-5 text-green-600" />;
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Recommendations</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {recommendations.length === 0 ? (
          <Alert>
            <CheckCircle2 className="h-4 w-4" />
            <AlertDescription>
              No recommendations at this time. Your site is in great shape!
            </AlertDescription>
          </Alert>
        ) : (
          recommendations.map((rec, index) => (
            <div
              key={index}
              className="border rounded-lg p-4 space-y-2 hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-start gap-3">
                {getPriorityIcon(rec.priority)}
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2">
                    <h4 className="font-semibold">{rec.title}</h4>
                    <Badge variant={getPriorityVariant(rec.priority)}>
                      {rec.priority.toUpperCase()}
                    </Badge>
                    <Badge variant="outline">{rec.category}</Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">{rec.description}</p>
                  <p className="text-xs text-muted-foreground italic">
                    Impact: {rec.impact}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </CardContent>
    </Card>
  );
}
