import React, { useEffect, useRef } from 'react';
import { Link, LinkProps } from 'react-router-dom';
import { useIntersectionObserver } from '@/lib/hooks/useIntersectionObserver';

interface PrefetchLinkProps extends LinkProps {
  prefetch?: 'hover' | 'visible' | 'none';
  children: React.ReactNode;
}

/**
 * Enhanced Link component with prefetching capabilities
 * Prefetches route data when link is hovered or becomes visible
 * 
 * @param prefetch - When to prefetch: 'hover', 'visible', or 'none'
 */
export const PrefetchLink: React.FC<PrefetchLinkProps> = ({
  prefetch = 'hover',
  to,
  children,
  ...props
}) => {
  const linkRef = useRef<HTMLAnchorElement>(null);
  const { ref: observerRef, isVisible } = useIntersectionObserver<HTMLAnchorElement>({
    threshold: 0.1,
    freezeOnceVisible: true,
  });
  
  const prefetchRoute = () => {
    // In a real implementation, this would prefetch route data
    // For now, we'll just create a prefetch link element
    const href = typeof to === 'string' ? to : to.pathname || '';
    
    if (!href) return;
    
    // Check if prefetch link already exists
    const existingLink = document.querySelector(`link[rel="prefetch"][href="${href}"]`);
    if (existingLink) return;
    
    // Create prefetch link
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = href;
    document.head.appendChild(link);
  };

  // Prefetch on visibility
  useEffect(() => {
    if (prefetch === 'visible' && isVisible) {
      prefetchRoute();
    }
  }, [prefetch, isVisible]);

  const handleMouseEnter = () => {
    if (prefetch === 'hover') {
      prefetchRoute();
    }
  };

  // Combine refs using callback ref pattern
  const setRefs = (element: HTMLAnchorElement | null) => {
    // @ts-ignore - We need to set both refs
    linkRef.current = element;
    // @ts-ignore - We need to set both refs
    observerRef.current = element;
  };

  return (
    <Link
      ref={setRefs}
      to={to}
      onMouseEnter={handleMouseEnter}
      {...props}
    >
      {children}
    </Link>
  );
};
