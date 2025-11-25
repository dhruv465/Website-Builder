import * as React from 'react';
import { cn } from '../../lib/utils';

export interface ResponsiveTextareaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  /**
   * Whether to disable autocomplete, autocorrect, and autocapitalize
   */
  disableAutoFeatures?: boolean;
  
  /**
   * Whether to auto-resize based on content
   */
  autoResize?: boolean;
}

const ResponsiveTextarea = React.forwardRef<HTMLTextAreaElement, ResponsiveTextareaProps>(
  ({ className, disableAutoFeatures = false, autoResize = false, ...props }, ref) => {
    const textareaRef = React.useRef<HTMLTextAreaElement | null>(null);

    // Handle auto-resize
    React.useEffect(() => {
      if (!autoResize || !textareaRef.current) return;

      const textarea = textareaRef.current;
      
      const handleResize = () => {
        textarea.style.height = 'auto';
        textarea.style.height = `${textarea.scrollHeight}px`;
      };

      textarea.addEventListener('input', handleResize);
      handleResize(); // Initial resize

      return () => {
        textarea.removeEventListener('input', handleResize);
      };
    }, [autoResize]);

    // Combine refs
    const setRefs = React.useCallback(
      (node: HTMLTextAreaElement | null) => {
        textareaRef.current = node;
        if (typeof ref === 'function') {
          ref(node);
        } else if (ref) {
          ref.current = node;
        }
      },
      [ref]
    );

    // Mobile optimization props
    const mobileOptimizedProps = {
      // Prevent iOS zoom on focus
      style: { fontSize: '16px' },
      
      // Disable auto-features if requested
      ...(disableAutoFeatures && {
        autoComplete: 'off',
        autoCorrect: 'off',
        autoCapitalize: 'off',
        spellCheck: false,
      }),
    };

    return (
      <textarea
        className={cn(
          'flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2',
          'text-base ring-offset-background',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          // Responsive text size
          'sm:text-sm',
          // Auto-resize handling
          autoResize && 'resize-none overflow-hidden',
          className
        )}
        ref={setRefs}
        {...mobileOptimizedProps}
        {...props}
      />
    );
  }
);

ResponsiveTextarea.displayName = 'ResponsiveTextarea';

export { ResponsiveTextarea };
