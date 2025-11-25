import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ScoreCardProps {
  title: string;
  score: number;
  passedChecks: number;
  totalChecks: number;
  className?: string;
}

export function ScoreCard({
  title,
  score,
  passedChecks,
  totalChecks,
  className,
}: ScoreCardProps) {
  // Determine color based on score
  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 70) return 'text-yellow-600';
    if (score >= 50) return 'text-orange-600';
    return 'text-red-600';
  };

  const getStrokeColor = (score: number) => {
    if (score >= 90) return 'stroke-green-600';
    if (score >= 70) return 'stroke-yellow-600';
    if (score >= 50) return 'stroke-orange-600';
    return 'stroke-red-600';
  };

  // Calculate circle properties
  const radius = 45;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <Card className={cn('flex-1', className)}>
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        {/* Circular Progress Indicator */}
        <div className="relative w-32 h-32">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            {/* Background circle */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className="stroke-muted fill-none"
              strokeWidth="8"
            />
            {/* Progress circle */}
            <circle
              cx="50"
              cy="50"
              r={radius}
              className={cn('fill-none transition-all duration-500', getStrokeColor(score))}
              strokeWidth="8"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
            />
          </svg>
          {/* Score text */}
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn('text-3xl font-bold', getScoreColor(score))}>
              {Math.round(score)}
            </span>
          </div>
        </div>

        {/* Checks summary */}
        <div className="mt-4 text-center">
          <p className="text-sm text-muted-foreground">
            {passedChecks} of {totalChecks} checks passed
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
