/**
 * Performance optimization utilities
 */

/**
 * Generate srcset for responsive images
 * @param src - Base image URL
 * @param widths - Array of widths to generate
 * @returns srcset string
 */
export function generateSrcSet(src: string, widths: number[] = [320, 640, 960, 1280, 1920]): string {
  return widths
    .map((width) => {
      const url = src.replace(/\.(jpg|jpeg|png|webp)$/i, `-${width}w.$1`);
      return `${url} ${width}w`;
    })
    .join(', ');
}

/**
 * Generate sizes attribute for responsive images
 * @param breakpoints - Object mapping breakpoints to sizes
 * @returns sizes string
 */
export function generateSizes(
  breakpoints: Record<string, string> = {
    '(max-width: 640px)': '100vw',
    '(max-width: 1024px)': '50vw',
    default: '33vw',
  }
): string {
  const entries = Object.entries(breakpoints);
  const mediaQueries = entries
    .filter(([key]) => key !== 'default')
    .map(([query, size]) => `${query} ${size}`);
  
  const defaultSize = breakpoints.default || '100vw';
  return [...mediaQueries, defaultSize].join(', ');
}

/**
 * Preload critical resources
 * @param resources - Array of resource URLs to preload
 * @param type - Resource type (image, font, script, style)
 */
export function preloadResources(
  resources: string[],
  type: 'image' | 'font' | 'script' | 'style' = 'image'
): void {
  resources.forEach((url) => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.href = url;
    link.as = type;
    
    if (type === 'font') {
      link.crossOrigin = 'anonymous';
    }
    
    document.head.appendChild(link);
  });
}

/**
 * Prefetch resources for anticipated navigation
 * @param urls - Array of URLs to prefetch
 */
export function prefetchResources(urls: string[]): void {
  urls.forEach((url) => {
    const link = document.createElement('link');
    link.rel = 'prefetch';
    link.href = url;
    document.head.appendChild(link);
  });
}

/**
 * Check if browser supports WebP format
 * @returns Promise that resolves to boolean
 */
export async function supportsWebP(): Promise<boolean> {
  if (!window.createImageBitmap) return false;

  const webpData = 'data:image/webp;base64,UklGRh4AAABXRUJQVlA4TBEAAAAvAAAAAAfQ//73v/+BiOh/AAA=';
  
  try {
    const blob = await fetch(webpData).then((r) => r.blob());
    return await createImageBitmap(blob).then(() => true, () => false);
  } catch {
    return false;
  }
}

/**
 * Get optimized image URL based on browser support
 * @param src - Original image URL
 * @param _format - Preferred format (webp, avif) - currently unused
 * @returns Optimized image URL
 */
export function getOptimizedImageUrl(src: string, _format: 'webp' | 'avif' = 'webp'): string {
  // In a real app, this would check browser support and return appropriate format
  // For now, just return the original URL
  return src;
}

/**
 * Throttle function execution
 * @param func - Function to throttle
 * @param limit - Time limit in milliseconds
 * @returns Throttled function
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  
  return function (this: any, ...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}

/**
 * Debounce function execution
 * @param func - Function to debounce
 * @param delay - Delay in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout;
  
  return function (this: any, ...args: Parameters<T>) {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(this, args), delay);
  };
}

/**
 * Request idle callback with fallback
 * @param callback - Function to execute during idle time
 * @param options - Idle callback options
 */
export function requestIdleCallback(
  callback: () => void,
  options?: { timeout?: number }
): number {
  if ('requestIdleCallback' in window) {
    return window.requestIdleCallback(callback, options);
  }
  
  // Fallback for browsers that don't support requestIdleCallback
  return setTimeout(callback, 1) as unknown as number;
}

/**
 * Cancel idle callback with fallback
 * @param id - Callback ID to cancel
 */
export function cancelIdleCallback(id: number): void {
  if ('cancelIdleCallback' in window) {
    window.cancelIdleCallback(id);
  } else {
    clearTimeout(id);
  }
}
