import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import {
  ArrowLeft,
  ExternalLink,
  Edit,
  Trash2,
  Copy,
  Download,
  Play,
  BarChart3,
} from 'lucide-react';
import AnimatedPage from '../components/shared/AnimatedPage';
import { VersionHistory } from '../components/project';
import { DeploymentPanel } from '../components/deployment';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Separator } from '../components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { useSession } from '../lib/context/SessionContext';
import { LoadingSpinner } from '../components/ui/loading-spinner';
import { Site } from '../lib/types';

export default function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const { session, isLoading } = useSession();
  const [site, setSite] = useState<Site | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  useEffect(() => {
    if (session?.sites && projectId) {
      const foundSite = session.sites.find((s) => s.id === projectId);
      setSite(foundSite || null);
    }
  }, [session, projectId]);

  const handleDelete = async () => {
    // TODO: Implement delete functionality
    console.log('Delete site:', projectId);
    setDeleteDialogOpen(false);
    navigate('/dashboard/projects');
  };

  const handleDuplicate = async () => {
    // TODO: Implement duplicate functionality
    console.log('Duplicate site:', projectId);
  };

  const handleExport = () => {
    if (!site) return;

    const exportData = {
      name: site.name,
      description: site.description,
      framework: site.framework,
      design_style: site.design_style,
      versions: site.versions,
      created_at: site.created_at,
      updated_at: site.updated_at,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${site.name || 'project'}-export.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleRestoreVersion = async (versionId: string) => {
    // TODO: Implement version restore functionality
    console.log('Restore version:', versionId);
  };

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (!site) {
    return (
      <AnimatedPage className="container mx-auto p-6 md:p-8">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="mb-4 text-6xl">🔍</div>
          <h2 className="mb-2 text-2xl font-bold">Project Not Found</h2>
          <p className="mb-6 text-muted-foreground">
            The project you're looking for doesn't exist or has been deleted.
          </p>
          <Button asChild>
            <Link to="/dashboard/projects">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Projects
            </Link>
          </Button>
        </div>
      </AnimatedPage>
    );
  }

  const latestVersion = site.versions?.[site.versions.length - 1];
  const latestAudit = site.audits?.[site.audits.length - 1];
  const latestDeployment = site.deployments?.find((d) => d.status === 'success');

  return (
    <AnimatedPage className="container mx-auto p-6 md:p-8">
      {/* Header */}
      <div className="mb-6">
        <Button variant="ghost" size="sm" asChild className="mb-4">
          <Link to="/dashboard/projects">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Projects
          </Link>
        </Button>

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex-1">
            <h1 className="mb-2 text-3xl font-bold">{site.name || 'Untitled Project'}</h1>
            <p className="text-muted-foreground">
              {site.description || 'No description provided'}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
              <Badge variant="secondary" className="capitalize">
                {site.framework}
              </Badge>
              <Badge variant="outline" className="capitalize">
                {site.design_style}
              </Badge>
              {latestDeployment && (
                <Badge variant="default">
                  <span className="mr-1 h-2 w-2 rounded-full bg-green-500"></span>
                  Deployed
                </Badge>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {latestDeployment && (
              <Button variant="default" asChild>
                <a href={latestDeployment.url} target="_blank" rel="noopener noreferrer">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  View Live
                </a>
              </Button>
            )}
            <Button variant="outline" asChild>
              <Link to={`/dashboard/builder/${site.id}`}>
                <Edit className="mr-2 h-4 w-4" />
                Edit
              </Link>
            </Button>
            <Button variant="outline" onClick={handleDuplicate}>
              <Copy className="mr-2 h-4 w-4" />
              Duplicate
            </Button>
            <Button variant="outline" onClick={handleExport}>
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Button variant="destructive" onClick={() => setDeleteDialogOpen(true)}>
              <Trash2 className="mr-2 h-4 w-4" />
              Delete
            </Button>
          </div>
        </div>
      </div>

      <Separator className="mb-6" />

      {/* Overview Cards */}
      <div className="mb-6 grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Versions</CardDescription>
            <CardTitle className="text-3xl">{site.versions?.length || 0}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Last updated {new Date(site.updated_at).toLocaleDateString()}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Latest Audit Score</CardDescription>
            <CardTitle className="text-3xl">
              {latestAudit ? latestAudit.overall_score : 'N/A'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {latestAudit
                ? `Audited ${new Date(latestAudit.timestamp).toLocaleDateString()}`
                : 'No audits yet'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardDescription>Deployments</CardDescription>
            <CardTitle className="text-3xl">{site.deployments?.length || 0}</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              {latestDeployment
                ? `Last deployed ${new Date(latestDeployment.created_at).toLocaleDateString()}`
                : 'Not deployed yet'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="versions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="versions">Version History</TabsTrigger>
          <TabsTrigger value="preview">Preview</TabsTrigger>
          <TabsTrigger value="audits">Audits</TabsTrigger>
          <TabsTrigger value="deployments">Deployments</TabsTrigger>
        </TabsList>

        <TabsContent value="versions" className="space-y-4">
          <VersionHistory
            versions={site.versions || []}
            onRestore={handleRestoreVersion}
          />
        </TabsContent>

        <TabsContent value="preview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Live Preview</CardTitle>
              <CardDescription>
                Preview of the current version (v{latestVersion?.version_number || 1})
              </CardDescription>
            </CardHeader>
            <CardContent>
              {latestVersion ? (
                <div className="aspect-video w-full overflow-hidden rounded-lg border">
                  <iframe
                    srcDoc={latestVersion.html_code}
                    className="h-full w-full"
                    sandbox="allow-scripts"
                    title="Site preview"
                  />
                </div>
              ) : (
                <div className="flex aspect-video items-center justify-center rounded-lg border bg-muted">
                  <p className="text-muted-foreground">No preview available</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audits" className="space-y-4">
          {site.audits && site.audits.length > 0 ? (
            <div className="space-y-4">
              {site.audits
                .slice()
                .reverse()
                .map((audit) => (
                  <Card key={audit.id}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle>Audit Report</CardTitle>
                          <CardDescription>
                            {new Date(audit.timestamp).toLocaleString()}
                          </CardDescription>
                        </div>
                        <Badge
                          variant={audit.overall_score >= 80 ? 'default' : 'destructive'}
                          className="text-lg"
                        >
                          {audit.overall_score}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4 md:grid-cols-3">
                        <div>
                          <p className="mb-1 text-sm font-medium">SEO</p>
                          <p className="text-2xl font-bold">{audit.seo.score}</p>
                          <p className="text-xs text-muted-foreground">
                            {audit.seo.issues.length} issue{audit.seo.issues.length !== 1 ? 's' : ''}
                          </p>
                        </div>
                        <div>
                          <p className="mb-1 text-sm font-medium">Accessibility</p>
                          <p className="text-2xl font-bold">{audit.accessibility.score}</p>
                          <p className="text-xs text-muted-foreground">
                            {audit.accessibility.issues.length} issue
                            {audit.accessibility.issues.length !== 1 ? 's' : ''}
                          </p>
                        </div>
                        <div>
                          <p className="mb-1 text-sm font-medium">Performance</p>
                          <p className="text-2xl font-bold">{audit.performance.score}</p>
                          <p className="text-xs text-muted-foreground">
                            {audit.performance.issues.length} issue
                            {audit.performance.issues.length !== 1 ? 's' : ''}
                          </p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
            </div>
          ) : (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <BarChart3 className="mb-4 h-12 w-12 text-muted-foreground" />
                <p className="mb-4 text-center text-muted-foreground">
                  No audits have been run for this project yet
                </p>
                <Button>
                  <Play className="mr-2 h-4 w-4" />
                  Run Audit
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="deployments" className="space-y-4">
          <DeploymentPanel
            siteId={site.id}
            siteName={site.name}
            initialDeployments={site.deployments || []}
          />
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Project?</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{site.name || 'this project'}"? This action cannot
              be undone. All versions, audits, and deployments will be permanently removed.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete Project
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </AnimatedPage>
  );
}
