import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  CheckCircle2,
  XCircle,
  Loader2,
  ExternalLink,
  Copy,
  AlertCircle,
} from 'lucide-react';
import type { Deployment } from '@/lib/types';
import { getDeploymentStatus } from '@/lib/api/deploy';

interface DeploymentStatusProps {
  deployment: Deployment;
  onRefresh?: () => void;
}

export function DeploymentStatus({ deployment, onRefresh }: DeploymentStatusProps) {
  const [currentDeployment, setCurrentDeployment] = useState(deployment);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    setCurrentDeployment(deployment);
  }, [deployment]);

  // Poll for status updates if deployment is in progress
  useEffect(() => {
    if (
      currentDeployment.status === 'pending' ||
      currentDeployment.status === 'deploying'
    ) {
      const interval = setInterval(async () => {
        try {
          const updated = await getDeploymentStatus(currentDeployment.id);
          setCurrentDeployment(updated);

          if (updated.status === 'success' || updated.status === 'failed') {
            clearInterval(interval);
            onRefresh?.();
          }
        } catch (error) {
          console.error('Failed to fetch deployment status:', error);
        }
      }, 5000);

      return () => {
        clearInterval(interval);
      };
    }
  }, [currentDeployment.id, currentDeployment.status, onRefresh]);

  const getStatusIcon = () => {
    switch (currentDeployment.status) {
      case 'success':
        return <CheckCircle2 className="h-5 w-5 text-green-500" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'deploying':
      case 'pending':
        return <Loader2 className="h-5 w-5 text-blue-500 animate-spin" />;
      default:
        return null;
    }
  };

  const getStatusBadge = () => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      pending: 'secondary',
      deploying: 'default',
      success: 'default',
      failed: 'destructive',
    };

    return (
      <Badge variant={variants[currentDeployment.status] || 'outline'}>
        {currentDeployment.status.toUpperCase()}
      </Badge>
    );
  };

  const getProgress = () => {
    switch (currentDeployment.status) {
      case 'pending':
        return 10;
      case 'deploying':
        return 50;
      case 'success':
        return 100;
      case 'failed':
        return 0;
      default:
        return 0;
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <CardTitle className="text-lg">Deployment Status</CardTitle>
          </div>
          {getStatusBadge()}
        </div>
        <CardDescription>
          Platform: {currentDeployment.platform} • Created: {formatDate(currentDeployment.created_at)}
        </CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Progress Bar */}
        {(currentDeployment.status === 'pending' ||
          currentDeployment.status === 'deploying') && (
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">
                {currentDeployment.status === 'pending'
                  ? 'Initializing deployment...'
                  : 'Deploying your site...'}
              </span>
              <span className="font-medium">{getProgress()}%</span>
            </div>
            <Progress value={getProgress()} className="h-2" />
          </div>
        )}

        {/* Success State */}
        {currentDeployment.status === 'success' && (
          <Alert className="border-green-500 bg-green-50 dark:bg-green-950">
            <CheckCircle2 className="h-4 w-4 text-green-500" />
            <AlertTitle className="text-green-700 dark:text-green-400">
              Deployment Successful!
            </AlertTitle>
            <AlertDescription className="text-green-600 dark:text-green-300">
              Your site is now live and accessible at the URL below.
              {currentDeployment.deployed_at && (
                <div className="mt-1 text-sm">
                  Deployed at: {formatDate(currentDeployment.deployed_at)}
                </div>
              )}
            </AlertDescription>
          </Alert>
        )}

        {/* Live URL */}
        {currentDeployment.status === 'success' && currentDeployment.url && (
          <div className="space-y-2">
            <label className="text-sm font-medium">Live URL</label>
            <div className="flex gap-2">
              <div className="flex-1 rounded-md border bg-muted px-3 py-2 text-sm font-mono">
                {currentDeployment.url}
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => copyToClipboard(currentDeployment.url)}
                title="Copy URL"
              >
                {copied ? (
                  <CheckCircle2 className="h-4 w-4" />
                ) : (
                  <Copy className="h-4 w-4" />
                )}
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => window.open(currentDeployment.url, '_blank')}
                title="Open in new tab"
              >
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}

        {/* Error State */}
        {currentDeployment.status === 'failed' && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Deployment Failed</AlertTitle>
            <AlertDescription>
              {currentDeployment.error_message || 'An unknown error occurred during deployment.'}
              <div className="mt-3 space-y-2">
                <p className="font-medium">Troubleshooting Tips:</p>
                <ul className="list-disc list-inside space-y-1 text-sm">
                  <li>Check that your build command is correct</li>
                  <li>Verify environment variables are properly set</li>
                  <li>Ensure output directory contains valid files</li>
                  <li>Review deployment logs for specific errors</li>
                </ul>
              </div>
            </AlertDescription>
          </Alert>
        )}

        {/* Deployment ID */}
        <div className="text-xs text-muted-foreground">
          Deployment ID: {currentDeployment.id}
        </div>
      </CardContent>
    </Card>
  );
}
