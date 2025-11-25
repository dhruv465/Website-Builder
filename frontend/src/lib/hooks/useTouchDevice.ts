import { useState, useEffect } from 'react';

/**
 * Hook to detect if the device supports touch input
 * @returns boolean indicating if touch is supported
 */
export function useTouchDevice(): boolean {
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    const checkTouchDevice = () => {
      // Check for touch support
      const hasTouch = 
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-ignore - for older browsers
        navigator.msMaxTouchPoints > 0;
      
      setIsTouchDevice(hasTouch);
    };

    checkTouchDevice();
    
    // Re-check on resize (for hybrid devices)
    window.addEventListener('resize', checkTouchDevice);
    
    return () => {
      window.removeEventListener('resize', checkTouchDevice);
    };
  }, []);

  return isTouchDevice;
}

/**
 * Hook to detect viewport size category
 * @returns 'mobile' | 'tablet' | 'desktop'
 */
export function useViewportSize(): 'mobile' | 'tablet' | 'desktop' {
  const [viewportSize, setViewportSize] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');

  useEffect(() => {
    const checkViewportSize = () => {
      const width = window.innerWidth;
      
      if (width < 768) {
        setViewportSize('mobile');
      } else if (width < 1024) {
        setViewportSize('tablet');
      } else {
        setViewportSize('desktop');
      }
    };

    checkViewportSize();
    
    window.addEventListener('resize', checkViewportSize);
    
    return () => {
      window.removeEventListener('resize', checkViewportSize);
    };
  }, []);

  return viewportSize;
}

/**
 * Hook to detect device orientation
 * @returns 'portrait' | 'landscape'
 */
export function useOrientation(): 'portrait' | 'landscape' {
  const [orientation, setOrientation] = useState<'portrait' | 'landscape'>(
    window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
  );

  useEffect(() => {
    const handleOrientationChange = () => {
      setOrientation(
        window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
      );
    };

    window.addEventListener('resize', handleOrientationChange);
    window.addEventListener('orientationchange', handleOrientationChange);

    return () => {
      window.removeEventListener('resize', handleOrientationChange);
      window.removeEventListener('orientationchange', handleOrientationChange);
    };
  }, []);

  return orientation;
}
