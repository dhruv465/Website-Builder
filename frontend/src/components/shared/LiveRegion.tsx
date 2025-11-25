import { useEffect, useRef } from 'react';

interface LiveRegionProps {
  message: string;
  priority?: 'polite' | 'assertive';
  clearOnUnmount?: boolean;
}

/**
 * ARIA live region component for announcing dynamic content changes
 * @param message - The message to announce to screen readers
 * @param priority - 'polite' (default) or 'assertive' for urgent announcements
 * @param clearOnUnmount - Whether to clear the message when component unmounts
 */
export default function LiveRegion({
  message,
  priority = 'polite',
  clearOnUnmount = true,
}: LiveRegionProps) {
  const regionRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (regionRef.current && message) {
      // Clear first to ensure screen readers pick up the change
      regionRef.current.textContent = '';
      
      // Set the message after a brief delay
      const timeoutId = setTimeout(() => {
        if (regionRef.current) {
          regionRef.current.textContent = message;
        }
      }, 100);

      return () => clearTimeout(timeoutId);
    }
  }, [message]);

  useEffect(() => {
    return () => {
      if (clearOnUnmount && regionRef.current) {
        regionRef.current.textContent = '';
      }
    };
  }, [clearOnUnmount]);

  return (
    <div
      ref={regionRef}
      role={priority === 'assertive' ? 'alert' : 'status'}
      aria-live={priority}
      aria-atomic="true"
      className="sr-only"
    />
  );
}
