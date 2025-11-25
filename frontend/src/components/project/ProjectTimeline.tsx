import { Link } from 'react-router-dom';
import { Calendar, ExternalLink, Copy, Trash2, Download, MoreVertical } from 'lucide-react';
import { Site } from '../../lib/types';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';

interface ProjectTimelineProps {
  sites: Site[];
  onDuplicate?: (siteId: string) => void;
  onDelete?: (siteId: string) => void;
  onExport?: (siteId: string) => void;
}

export default function ProjectTimeline({ sites, onDuplicate, onDelete, onExport }: ProjectTimelineProps) {
  if (sites.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 text-6xl">📅</div>
        <h3 className="mb-2 text-lg font-semibold">No projects found</h3>
        <p className="text-sm text-muted-foreground">
          Try adjusting your search or filters
        </p>
      </div>
    );
  }

  // Group sites by date
  const groupedSites = sites.reduce((acc, site) => {
    const date = new Date(site.updated_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
    if (!acc[date]) {
      acc[date] = [];
    }
    acc[date].push(site);
    return acc;
  }, {} as Record<string, Site[]>);

  const latestDeployment = (site: Site) => site.deployments?.find((d) => d.status === 'success');

  return (
    <div className="space-y-8">
      {Object.entries(groupedSites).map(([date, dateSites]) => (
        <div key={date}>
          <div className="mb-4 flex items-center gap-2 text-sm font-semibold text-muted-foreground">
            <Calendar className="h-4 w-4" />
            {date}
          </div>
          <div className="space-y-4 border-l-2 border-border pl-6">
            {dateSites.map((site) => (
              <div key={site.id} className="group relative">
                <div className="absolute -left-[1.6rem] top-3 h-3 w-3 rounded-full border-2 border-primary bg-background"></div>
                <div className="rounded-lg border bg-card p-4 transition-all hover:shadow-md">
                  <div className="flex items-start justify-between gap-4">
                    <Link to={`/dashboard/projects/${site.id}`} className="flex-1 min-w-0">
                      <h3 className="mb-1 font-semibold hover:text-primary">
                        {site.name || 'Untitled Project'}
                      </h3>
                      <p className="mb-3 line-clamp-2 text-sm text-muted-foreground">
                        {site.description || 'No description provided'}
                      </p>
                    </Link>

                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8 opacity-0 group-hover:opacity-100">
                          <MoreVertical className="h-4 w-4" />
                          <span className="sr-only">Open menu</span>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        {latestDeployment(site) && (
                          <>
                            <DropdownMenuItem asChild>
                              <a href={latestDeployment(site)!.url} target="_blank" rel="noopener noreferrer">
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

                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary" className="capitalize">
                      {site.framework}
                    </Badge>
                    <Badge variant="outline" className="capitalize">
                      {site.design_style}
                    </Badge>
                    {site.versions && site.versions.length > 0 && (
                      <Badge variant="outline">
                        {site.versions.length} version{site.versions.length !== 1 ? 's' : ''}
                      </Badge>
                    )}
                    {latestDeployment(site) && (
                      <Badge variant="default" className="ml-auto">
                        <span className="mr-1 h-2 w-2 rounded-full bg-green-500"></span>
                        Deployed
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
