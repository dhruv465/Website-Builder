import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { WebsiteBuilderInterface } from '@/components/builder/WebsiteBuilderInterface';
import { toast } from 'sonner';

interface Page {
  id: string;
  title: string;
  content: {
    id: string;
    title: string;
    heading: string;
    body: string;
    image: string;
    settings: Record<string, any>;
  };
}

export function WebsiteBuilderPage() {
  const navigate = useNavigate();
  const [isPublishing, setIsPublishing] = useState(false);

  const handleSave = async (pages: Page[]) => {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    console.log('Saving pages:', pages);
    toast.success('Changes saved successfully!');
  };

  const handlePublish = async () => {
    setIsPublishing(true);
    try {
      // Simulate publish API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('Website published successfully!', {
        description: 'Your website is now live at https://your-site.lovable.app',
      });
    } catch (error) {
      toast.error('Failed to publish website');
    } finally {
      setIsPublishing(false);
    }
  };

  const handleBack = () => {
    navigate('/dashboard');
  };

  return (
    <WebsiteBuilderInterface
      projectName="My Awesome Website"
      onSave={handleSave}
      onPublish={handlePublish}
      onBack={handleBack}
      autoSaveInterval={3000}
    />
  );
}
