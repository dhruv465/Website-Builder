// BuilderPage.tsx - Simplified version
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import StudioLayout from '@/layouts/StudioLayout';
import { RightPanel } from '@/components/layout/RightPanel';
import { Dialog, DialogContent } from '@/components/ui/dialog';
import { TemplateLibrary } from '@/components/templates/TemplateLibrary';
import { WelcomeModal } from '@/components/onboarding/WelcomeModal';
import { GuidedTour } from '@/components/onboarding/GuidedTour';

export default function BuilderPage() {
  const { siteId } = useParams<{ siteId?: string }>();
  const navigate = useNavigate();

  // UI state
  const [isTemplateLibraryOpen, setIsTemplateLibraryOpen] = useState(false);
  const [showWelcome, setShowWelcome] = useState(false);
  const [showTour, setShowTour] = useState(false);

  // Show welcome modal on first visit
  useEffect(() => {
    const hasSeen = localStorage.getItem('hasSeenWelcome');
    if (!hasSeen) setShowWelcome(true);
  }, []);

  const handleStartTour = () => {
    setShowWelcome(false);
    setShowTour(true);
    localStorage.setItem('hasSeenWelcome', 'true');
  };
  const handleSkipWelcome = () => {
    setShowWelcome(false);
    localStorage.setItem('hasSeenWelcome', 'true');
  };
  const handleTourComplete = () => setShowTour(false);

  const handleTemplateSelect = (template: any) => {
    console.log('Selected template', template);
    setIsTemplateLibraryOpen(false);
  };

  return (
    <StudioLayout sidebar={null} rightPanel={<RightPanel />}> 
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-4">AI Builder</h1>
        <p>Select a template to start building your website.</p>
        {/* Template Library Dialog */}
        <Dialog open={isTemplateLibraryOpen} onOpenChange={setIsTemplateLibraryOpen}>
          <DialogContent className="max-w-6xl h-[90vh] p-0">
            <TemplateLibrary
              onSelectTemplate={handleTemplateSelect}
              onClose={() => setIsTemplateLibraryOpen(false)}
            />
          </DialogContent>
        </Dialog>
        {/* Welcome Modal */}
        <WelcomeModal
          open={showWelcome}
          onOpenChange={setShowWelcome}
          onStartTour={handleStartTour}
          onSkip={handleSkipWelcome}
        />
        {/* Guided Tour */}
        <GuidedTour isActive={showTour} onComplete={handleTourComplete} />
      </div>
    </StudioLayout>
  );
}
