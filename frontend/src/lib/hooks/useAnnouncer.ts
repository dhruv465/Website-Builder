import { useEffect, useRef } from 'react';

type AnnouncementPriority = 'polite' | 'assertive';

/**
 * Custom hook for creating ARIA live region announcements
 * Useful for announcing dynamic content changes to screen readers
 */
export function useAnnouncer() {
  const politeRegionRef = useRef<HTMLDivElement | null>(null);
  const assertiveRegionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    // Create polite live region if it doesn't exist
    if (!politeRegionRef.current) {
      const politeRegion = document.createElement('div');
      politeRegion.setAttribute('role', 'status');
      politeRegion.setAttribute('aria-live', 'polite');
      politeRegion.setAttribute('aria-atomic', 'true');
      politeRegion.className = 'sr-only';
      document.body.appendChild(politeRegion);
      politeRegionRef.current = politeRegion;
    }

    // Create assertive live region if it doesn't exist
    if (!assertiveRegionRef.current) {
      const assertiveRegion = document.createElement('div');
      assertiveRegion.setAttribute('role', 'alert');
      assertiveRegion.setAttribute('aria-live', 'assertive');
      assertiveRegion.setAttribute('aria-atomic', 'true');
      assertiveRegion.className = 'sr-only';
      document.body.appendChild(assertiveRegion);
      assertiveRegionRef.current = assertiveRegion;
    }

    return () => {
      // Cleanup on unmount
      if (politeRegionRef.current) {
        document.body.removeChild(politeRegionRef.current);
        politeRegionRef.current = null;
      }
      if (assertiveRegionRef.current) {
        document.body.removeChild(assertiveRegionRef.current);
        assertiveRegionRef.current = null;
      }
    };
  }, []);

  const announce = (message: string, priority: AnnouncementPriority = 'polite') => {
    const region = priority === 'assertive' ? assertiveRegionRef.current : politeRegionRef.current;
    
    if (region) {
      // Clear the region first to ensure the announcement is read
      region.textContent = '';
      
      // Use setTimeout to ensure the screen reader picks up the change
      setTimeout(() => {
        region.textContent = message;
      }, 100);
    }
  };

  return { announce };
}
