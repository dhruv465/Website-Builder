import * as React from 'react';
import { cn } from '@/lib/utils';
import { Label } from './label';

interface FormFieldProps {
  id: string;
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: React.ReactElement;
  className?: string;
}

/**
 * Accessible form field component with proper ARIA associations
 * Automatically links labels, errors, and hints to the input element
 */
export function FormField({
  id,
  label,
  error,
  hint,
  required = false,
  children,
  className,
}: FormFieldProps) {
  const errorId = `${id}-error`;
  const hintId = `${id}-hint`;
  
  // Build aria-describedby string
  const describedBy = [
    hint ? hintId : null,
    error ? errorId : null,
  ]
    .filter(Boolean)
    .join(' ');

  // Clone the child element and add accessibility props
  const childWithProps = React.cloneElement(children, {
    id,
    'aria-invalid': error ? 'true' : 'false',
    'aria-describedby': describedBy || undefined,
    'aria-required': required ? 'true' : 'false',
  });

  return (
    <div className={cn('space-y-2', className)}>
      <Label htmlFor={id}>
        {label}
        {required && (
          <span className="ml-1 text-destructive" aria-label="required">
            *
          </span>
        )}
      </Label>
      
      {hint && (
        <p id={hintId} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
      
      {childWithProps}
      
      {error && (
        <p
          id={errorId}
          className="text-sm font-medium text-destructive"
          role="alert"
          aria-live="polite"
        >
          {error}
        </p>
      )}
    </div>
  );
}
