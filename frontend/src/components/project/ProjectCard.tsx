import React, { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { MoreVertical, ExternalLink, Copy, Trash2, Download } from 'lucide-react';
import { motion, useReducedMotion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { cardHoverVariants } from '@/lib/utils/animations';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import { Badge } from '../ui/badge';
import { Site } from '../../lib/types';

interface ProjectCardProps {
  site: Site;
  onDuplicate?: (siteId: string) => void;
  onDelete?: (siteId: string) => void;
  onExport?: (siteId: string) => void;
}

// Memoized component to prevent unnecessary re-renders
const ProjectCard = React.memo<ProjectCardProps>(({ site, onDuplicate, onDelete, onExport }) => {
  // Memoize expensive computations
  const latestAudit = useMemo(() => site.audits?.[site.audits.length - 1], [site.audits]);
  const latestDeployment = useMemo(
    () => site.deployments?.find((d) => d.status === 'success'),
    [site.deployments]
  );
  const versionCount = useMemo(() => site.versions?.length || 0, [site.versions]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    return date.toLocaleDateString();
  };

  const prefersReducedMotion = useReducedMotion();
  const MotionCard = motion(Card);

  return (
    <MotionCard
      initial="rest"
      whileHover={!prefersReducedMotion ? 'hover' : undefined}
      variants={cardHoverVariants}
      className="group relative overflow-hidden transition-shadow hover:shadow-lg"
    >
      <Link to={`/dashboard/projects/${site.id}`}>
        <div className="aspect-video w-full overflow-hidden bg-gradient-to-br from-primary/10 to-primary/5">
          {/* Placeholder thumbnail - in a real app, this would be a screenshot */}
          <div className="flex h-full items-center justify-center">
            <div className="text-center">
              <div className="mb-2 text-4xl font-bold text-primary/20">
                {site.name?.charAt(0).toUpperCase() || 'P'}
              </div>
              <div className="text-xs text-muted-foreground">
                {versionCount} version{versionCount !== 1 ? 's' : ''}
              </div>
            </div>
          </div>
        </div>
      </Link>

      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <Link to={`/dashboard/projects/${site.id}`} className="flex-1 min-w-0">
            <CardTitle className="line-clamp-1 text-lg">{site.name || 'Untitled Project'}</CardTitle>
            <CardDescription className="line-clamp-2 mt-1">
              {site.description || 'No description provided'}
            </CardDescription>
          </Link>

          <DropdownMenu>
            <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
              <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100">
                <MoreVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              {latestDeployment && (
                <>
                  <DropdownMenuItem asChild>
                    <a href={latestDeployment.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="mr-2 h-4 w-4" />
                      View Live Site
                    </a>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                </>
              )}
              <DropdownMenuItem onClick={() => onDuplicate?.(site.id)}>
                <Copy className="mr-2 h-4 w-4" />
                Duplicate
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport?.(site.id)}>
                <Download className="mr-2 h-4 w-4" />
                Export
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => onDelete?.(site.id)}
                className="text-destructive focus:text-destructive"
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        <div className="flex flex-wrap gap-2 mb-3">
          <Badge variant="secondary" className="capitalize">
            {site.framework}
          </Badge>
          <Badge variant="outline" className="capitalize">
            {site.design_style}
          </Badge>
          {latestAudit && (
            <Badge
              variant={latestAudit.overall_score >= 80 ? 'default' : 'destructive'}
              className="ml-auto"
            >
              Score: {latestAudit.overall_score}
            </Badge>
          )}
        </div>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Updated {formatDate(site.updated_at)}</span>
          {latestDeployment && (
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-green-500"></span>
              Deployed
            </span>
          )}
        </div>
      </CardContent>
    </MotionCard>
  );
}
);

export default ProjectCard;
