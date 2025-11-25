import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle, Loader2 } from 'lucide-react';
import type { DeploymentConfig } from '@/lib/types';

const deploymentSchema = z.object({
  projectName: z.string().min(1, 'Project name is required').max(50),
  environmentVariables: z.string().optional(),
  buildCommand: z.string().optional(),
  outputDirectory: z.string().optional(),
});

type DeploymentFormData = z.infer<typeof deploymentSchema>;

interface DeploymentConfigDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDeploy: (config: DeploymentConfig) => Promise<void>;
  siteId: string;
  siteName?: string;
}

export function DeploymentConfigDialog({
  open,
  onOpenChange,
  onDeploy,
  siteId,
  siteName,
}: DeploymentConfigDialogProps) {
  const [isDeploying, setIsDeploying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<DeploymentFormData>({
    resolver: zodResolver(deploymentSchema),
    defaultValues: {
      projectName: siteName || `site-${siteId.slice(0, 8)}`,
      buildCommand: 'npm run build',
      outputDirectory: 'dist',
    },
  });

  const onSubmit = async (data: DeploymentFormData) => {
    setIsDeploying(true);
    setError(null);

    try {
      // Parse environment variables from string format
      const envVars: Record<string, string> = {};
      if (data.environmentVariables) {
        const lines = data.environmentVariables.split('\n');
        lines.forEach((line) => {
          const [key, ...valueParts] = line.split('=');
          if (key && valueParts.length > 0) {
            envVars[key.trim()] = valueParts.join('=').trim();
          }
        });
      }

      const config: DeploymentConfig = {
        platform: 'vercel',
        projectName: data.projectName,
        environmentVariables: Object.keys(envVars).length > 0 ? envVars : undefined,
        buildCommand: data.buildCommand || undefined,
        outputDirectory: data.outputDirectory || undefined,
      };

      await onDeploy(config);
      reset();
      onOpenChange(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start deployment');
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Deploy to Vercel</DialogTitle>
          <DialogDescription>
            Configure your deployment settings. Your site will be deployed to Vercel's platform.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="projectName">Project Name *</Label>
            <Input
              id="projectName"
              {...register('projectName')}
              placeholder="my-awesome-site"
              disabled={isDeploying}
            />
            {errors.projectName && (
              <p className="text-sm text-red-500">{errors.projectName.message}</p>
            )}
          </div>

          <div className="space-y-2">
            <Label htmlFor="buildCommand">Build Command</Label>
            <Input
              id="buildCommand"
              {...register('buildCommand')}
              placeholder="npm run build"
              disabled={isDeploying}
            />
            <p className="text-xs text-muted-foreground">
              Command to build your site (optional)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="outputDirectory">Output Directory</Label>
            <Input
              id="outputDirectory"
              {...register('outputDirectory')}
              placeholder="dist"
              disabled={isDeploying}
            />
            <p className="text-xs text-muted-foreground">
              Directory containing built files (optional)
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="environmentVariables">Environment Variables</Label>
            <textarea
              id="environmentVariables"
              {...register('environmentVariables')}
              className="flex min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              placeholder="API_KEY=your_key&#10;NODE_ENV=production"
              disabled={isDeploying}
            />
            <p className="text-xs text-muted-foreground">
              One variable per line in KEY=VALUE format (optional)
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isDeploying}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isDeploying}>
              {isDeploying && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Deploy
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
