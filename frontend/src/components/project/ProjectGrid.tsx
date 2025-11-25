import { Site } from '../../lib/types';
import ProjectCard from './ProjectCard';
import { AnimatedGrid, AnimatedGridItem } from '../shared/AnimatedGrid';

interface ProjectGridProps {
  sites: Site[];
  onDuplicate?: (siteId: string) => void;
  onDelete?: (siteId: string) => void;
  onExport?: (siteId: string) => void;
}

export default function ProjectGrid({ sites, onDuplicate, onDelete, onExport }: ProjectGridProps) {
  if (sites.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 text-6xl">📁</div>
        <h3 className="mb-2 text-lg font-semibold">No projects found</h3>
        <p className="text-sm text-muted-foreground">
          Try adjusting your search or filters
        </p>
      </div>
    );
  }

  return (
    <AnimatedGrid className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {sites.map((site) => (
        <AnimatedGridItem key={site.id}>
          <ProjectCard
            site={site}
            onDuplicate={onDuplicate}
            onDelete={onDelete}
            onExport={onExport}
          />
        </AnimatedGridItem>
      ))}
    </AnimatedGrid>
  );
}
