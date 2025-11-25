import * as React from 'react';
import { cn } from '../../lib/utils';

export interface ResponsiveInputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  /**
   * Input mode for mobile keyboards
   * - 'text': Standard keyboard
   * - 'email': Email keyboard with @ symbol
   * - 'tel': Numeric keyboard for phone numbers
   * - 'url': URL keyboard with .com shortcut
   * - 'numeric': Numeric keyboard
   * - 'decimal': Numeric keyboard with decimal point
   * - 'search': Search keyboard with search button
   */
  inputMode?: 'text' | 'email' | 'tel' | 'url' | 'numeric' | 'decimal' | 'search';
  
  /**
   * Whether to disable autocomplete, autocorrect, and autocapitalize
   */
  disableAutoFeatures?: boolean;
}

const ResponsiveInput = React.forwardRef<HTMLInputElement, ResponsiveInputProps>(
  ({ className, type, inputMode, disableAutoFeatures = false, ...props }, ref) => {
    // Set appropriate input attributes for mobile optimization
    const mobileOptimizedProps = {
      // Prevent iOS zoom on focus by ensuring font-size is at least 16px
      style: { fontSize: '16px' },
      
      // Set input mode for appropriate mobile keyboard
      inputMode: inputMode || (type === 'email' ? 'email' : type === 'tel' ? 'tel' : 'text'),
      
      // Disable auto-features if requested
      ...(disableAutoFeatures && {
        autoComplete: 'off',
        autoCorrect: 'off',
        autoCapitalize: 'off',
        spellCheck: false,
      }),
    };

    return (
      <input
        type={type}
        className={cn(
          'flex h-touch w-full rounded-md border border-input bg-background px-3 py-2',
          'text-base ring-offset-background',
          'file:border-0 file:bg-transparent file:text-sm file:font-medium',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
          // Touch-friendly sizing
          'min-h-touch',
          // Responsive text size
          'sm:text-sm',
          className
        )}
        ref={ref}
        {...mobileOptimizedProps}
        {...props}
      />
    );
  }
);

ResponsiveInput.displayName = 'ResponsiveInput';

export { ResponsiveInput };
