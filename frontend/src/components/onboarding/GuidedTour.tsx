import { useEffect } from 'react';
import { driver } from 'driver.js';
import 'driver.js/dist/driver.css';

interface GuidedTourProps {
  isActive: boolean;
  onComplete: () => void;
}

export function GuidedTour({ isActive, onComplete }: GuidedTourProps) {
  useEffect(() => {
    if (isActive) {
      const driverObj = driver({
        showProgress: true,
        animate: true,
        doneBtnText: 'Done',
        nextBtnText: 'Next',
        prevBtnText: 'Previous',
        onDestroyed: onComplete,
        steps: [
          {
            element: '#ai-input-container',
            popover: {
              title: 'AI Assistant',
              description: 'Start here! Describe the website you want to build, and our AI will generate the code for you.',
              side: 'right',
              align: 'start',
            },
          },
          {
            element: '#editor-tabs',
            popover: {
              title: 'Editor Modes',
              description: 'Switch between Code view for manual edits, Visual view for drag-and-drop, and Preview to see your site live.',
              side: 'bottom',
              align: 'start',
            },
          },
          {
            element: '#template-selector',
            popover: {
              title: 'Templates',
              description: 'Need inspiration? Choose from our collection of professional templates to get a head start.',
              side: 'right',
              align: 'start',
            },
          },
          {
            element: '#deployment-section',
            popover: {
              title: 'Deploy',
              description: 'Ready to go live? Deploy your website to the internet with a single click.',
              side: 'left',
              align: 'start',
            },
          },
          {
            element: '#export-tools',
            popover: {
              title: 'Export & SEO',
              description: 'Download your code, push to GitHub, or optimize your site for search engines.',
              side: 'top',
              align: 'start',
            },
          },
        ],
      });

      driverObj.drive();

      return () => {
        driverObj.destroy();
      };
    }
  }, [isActive, onComplete]);

  return null;
}
