import { useState } from 'react';
import { Clock, RotateCcw, Eye } from 'lucide-react';
import { SiteVersion } from '../../lib/types';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../ui/dialog';
import { ScrollArea } from '../ui/scroll-area';

interface VersionHistoryProps {
  versions: SiteVersion[];
  onRestore?: (versionId: string) => void;
}

export default function VersionHistory({ versions, onRestore }: VersionHistoryProps) {
  const [selectedVersion, setSelectedVersion] = useState<SiteVersion | null>(null);
  const [restoreDialogOpen, setRestoreDialogOpen] = useState(false);
  const [previewDialogOpen, setPreviewDialogOpen] = useState(false);

  const sortedVersions = [...versions].sort((a, b) => b.version_number - a.version_number);

  const handleRestore = (version: SiteVersion) => {
    setSelectedVersion(version);
    setRestoreDialogOpen(true);
  };

  const handlePreview = (version: SiteVersion) => {
    setSelectedVersion(version);
    setPreviewDialogOpen(true);
  };

  const confirmRestore = () => {
    if (selectedVersion && onRestore) {
      onRestore(selectedVersion.id);
      setRestoreDialogOpen(false);
      setSelectedVersion(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  if (versions.length === 0) {
    return (
      <Card>
        <CardContent className="flex flex-col items-center justify-center py-12">
          <Clock className="mb-4 h-12 w-12 text-muted-foreground" />
          <p className="text-center text-muted-foreground">No version history available</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <>
      <div className="space-y-4">
        {sortedVersions.map((version, index) => (
          <Card key={version.id} className={index === 0 ? 'border-primary' : ''}>
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <CardTitle className="text-base">Version {version.version_number}</CardTitle>
                    {index === 0 && <Badge>Current</Badge>}
                  </div>
                  <CardDescription className="mt-1">
                    {formatDate(version.created_at)}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handlePreview(version)}
                  >
                    <Eye className="mr-2 h-4 w-4" />
                    Preview
                  </Button>
                  {index !== 0 && (
                    <Button
                      variant="default"
                      size="sm"
                      onClick={() => handleRestore(version)}
                    >
                      <RotateCcw className="mr-2 h-4 w-4" />
                      Restore
                    </Button>
                  )}
                </div>
              </div>
            </CardHeader>
            {version.change_description && (
              <CardContent className="pt-0">
                <p className="text-sm text-muted-foreground">{version.change_description}</p>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* Restore Confirmation Dialog */}
      <Dialog open={restoreDialogOpen} onOpenChange={setRestoreDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Restore Version?</DialogTitle>
            <DialogDescription>
              Are you sure you want to restore to version {selectedVersion?.version_number}? This will
              create a new version with the content from the selected version.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRestoreDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={confirmRestore}>Restore Version</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Preview Dialog */}
      <Dialog open={previewDialogOpen} onOpenChange={setPreviewDialogOpen}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>Version {selectedVersion?.version_number} Preview</DialogTitle>
            <DialogDescription>
              Created on {selectedVersion && formatDate(selectedVersion.created_at)}
            </DialogDescription>
          </DialogHeader>
          <ScrollArea className="h-[500px] w-full rounded-md border">
            {selectedVersion && (
              <iframe
                srcDoc={selectedVersion.html_code}
                className="h-full w-full"
                sandbox="allow-scripts"
                title={`Version ${selectedVersion.version_number} preview`}
              />
            )}
          </ScrollArea>
          <DialogFooter>
            <Button variant="outline" onClick={() => setPreviewDialogOpen(false)}>
              Close
            </Button>
            {selectedVersion && sortedVersions.length > 0 && sortedVersions[0]?.id !== selectedVersion.id && (
              <Button
                onClick={() => {
                  setPreviewDialogOpen(false);
                  handleRestore(selectedVersion);
                }}
              >
                <RotateCcw className="mr-2 h-4 w-4" />
                Restore This Version
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
