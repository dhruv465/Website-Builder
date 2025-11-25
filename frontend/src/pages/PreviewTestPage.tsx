import React from 'react';
import { SitePreviewExample } from '@/components/builder';

export const PreviewTestPage: React.FC = () => {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">Site Preview Component Test</h1>
        <p className="text-muted-foreground">
          Testing the SitePreview component with interactive controls
        </p>
      </div>
      
      <SitePreviewExample />
    </div>
  );
};

export default PreviewTestPage;
