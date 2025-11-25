import { DeploymentPanel } from '@/components/deployment';

export default function DeploymentTestPage() {
  // Mock site data for testing
  const mockSiteId = 'test-site-123';
  const mockSiteName = 'My Test Website';

  return (
    <div className="container mx-auto py-8 px-4 max-w-6xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Deployment Test Page</h1>
        <p className="text-muted-foreground">
          Test the deployment interface and components
        </p>
      </div>

      <DeploymentPanel siteId={mockSiteId} siteName={mockSiteName} />
    </div>
  );
}
