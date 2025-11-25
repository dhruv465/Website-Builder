import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { Clock, RotateCcw, Eye } from 'lucide-react';
import { SiteVersion } from '@/lib/types/api';
import { cn } from '@/lib/utils';

export interface VersionHistoryProps {
  versions: SiteVersion[];
  currentVersionId?: string;
  onVersionRestore?: (version: SiteVersion) => void;
  onVersionPreview?: (version: SiteVersion) => void;
  className?: string;
}

export const VersionHistory: React.FC<VersionHistoryProps> = ({
  versions,
  currentVersionId,
  onVersionRestore,
  onVersionPreview,
  className,
}) => {
  const [sortedVersions, setSortedVersions] = useState<SiteVersion[]>([]);

  useEffect(() => {
    // Sort versions by version number descending (newest first)
    const sorted = [...versions].sort((a, b) => b.version_number - a.version_number);
    setSortedVersions(sorted);
  }, [versions]);

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;

    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: date.getFullYear() !== now.getFullYear() ? 'numeric' : undefined,
    });
  };

  const handleRestore = (version: SiteVersion) => {
    if (window.confirm(`Restore to version ${version.version_number}? This will create a new version.`)) {
      onVersionRestore?.(version);
    }
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Version History
        </CardTitle>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[400px] pr-4">
          {sortedVersions.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No version history available
            </div>
          ) : (
            <div className="space-y-3">
              {sortedVersions.map((version, index) => {
                const isCurrentVersion = version.id === currentVersionId;
                const isLatest = index === 0;

                return (
                  <div
                    key={version.id}
                    className={cn(
                      'p-3 border rounded-lg transition-colors',
                      isCurrentVersion && 'border-primary bg-primary/5'
                    )}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium">
                            Version {version.version_number}
                          </span>
                          {isLatest && (
                            <Badge variant="secondary" className="text-xs">
                              Latest
                            </Badge>
                          )}
                          {isCurrentVersion && (
                            <Badge variant="default" className="text-xs">
                              Current
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">
                          {formatDate(version.created_at)}
                        </p>
                        {version.change_description && (
                          <p className="text-sm text-muted-foreground line-clamp-2">
                            {version.change_description}
                          </p>
                        )}
                      </div>

                      <div className="flex items-center gap-1">
                        {onVersionPreview && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => onVersionPreview(version)}
                            title="Preview this version"
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                        )}
                        {onVersionRestore && !isCurrentVersion && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleRestore(version)}
                            title="Restore this version"
                          >
                            <RotateCcw className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </div>

                    {/* Version stats */}
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span>HTML: {version.html_code.length} chars</span>
                      {version.css_code && (
                        <span>CSS: {version.css_code.length} chars</span>
                      )}
                      {version.js_code && (
                        <span>JS: {version.js_code.length} chars</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </ScrollArea>
      </CardContent>
    </Card>
  );
};
