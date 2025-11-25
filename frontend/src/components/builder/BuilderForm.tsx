import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { ArrowRight } from 'lucide-react';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import { useLocalStorage, useDebounce } from '@/lib/hooks/useLocalStorage';
import { useKeyboardShortcut } from '@/lib/hooks/useKeyboardShortcut';
import { useAnnouncer } from '@/lib/hooks/useAnnouncer';
import { BuilderFormData } from '@/lib/types/site';
import { cn } from '@/lib/utils';

const builderFormSchema = z.object({
  requirements: z
    .string()
    .min(10, 'Please describe your website in at least 10 characters')
    .max(5000, 'Description is too long'),
  framework: z.enum(['react', 'vue', 'nextjs', 'html']).optional(),
  designStyle: z.enum(['modern', 'minimal', 'brutalist', 'glassmorphism', 'neomorphism', 'gradient', 'retro', 'cyberpunk']).optional(),
  features: z.array(z.string()).optional(),
  colorScheme: z.string().optional(),
});

interface BuilderFormProps {
  onSubmit: (data: BuilderFormData) => Promise<void>;
  initialData?: Partial<BuilderFormData>;
  isLoading?: boolean;
  className?: string;
}

const AUTOSAVE_DELAY = 1000;

const frameworks = [
  { id: 'react', name: 'React' },
  { id: 'vue', name: 'Vue' },
  { id: 'nextjs', name: 'Next.js' },
  { id: 'html', name: 'HTML' },
] as const;

const designStyles = [
  { id: 'modern', name: 'Modern' },
  { id: 'minimal', name: 'Minimal' },
  { id: 'brutalist', name: 'Brutalist' },
  { id: 'glassmorphism', name: 'Glassmorphism' },
  { id: 'neomorphism', name: 'Neomorphism' },
  { id: 'gradient', name: 'Gradient' },
  { id: 'retro', name: 'Retro' },
  { id: 'cyberpunk', name: 'Cyberpunk' },
] as const;

const features = [
  { id: 'contact-form', name: 'Contact Form' },
  { id: 'blog', name: 'Blog' },
  { id: 'gallery', name: 'Gallery' },
  { id: 'testimonials', name: 'Testimonials' },
  { id: 'pricing', name: 'Pricing' },
  { id: 'faq', name: 'FAQ' },
] as const;

export const BuilderForm: React.FC<BuilderFormProps> = ({
  onSubmit,
  initialData,
  isLoading = false,
  className,
}) => {
  const [savedFormData, setSavedFormData] = useLocalStorage<Partial<BuilderFormData>>(
    'builder-form-draft',
    initialData || {}
  );
  const { announce } = useAnnouncer();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<BuilderFormData>({
    resolver: zodResolver(builderFormSchema),
    defaultValues: {
      requirements: savedFormData.requirements || initialData?.requirements || '',
      framework: savedFormData.framework || initialData?.framework,
      designStyle: savedFormData.designStyle || initialData?.designStyle,
      features: savedFormData.features || initialData?.features || [],
      colorScheme: savedFormData.colorScheme || initialData?.colorScheme || '',
    },
  });

  const watchedValues = watch();
  const debouncedValues = useDebounce(watchedValues, AUTOSAVE_DELAY);

  useEffect(() => {
    if (debouncedValues.requirements || debouncedValues.framework) {
      setSavedFormData(debouncedValues);
    }
  }, [debouncedValues, setSavedFormData]);

  const requirements = watch('requirements') || '';
  const selectedFramework = watch('framework');
  const selectedDesignStyle = watch('designStyle');
  const selectedFeatures = watch('features') || [];

  const handleFormSubmit = async (data: BuilderFormData) => {
    try {
      announce('Generating website, please wait...', 'polite');
      await onSubmit(data);
      setSavedFormData({});
      announce('Website generation started successfully', 'polite');
    } catch (error) {
      console.error('Form submission error:', error);
      announce('Failed to generate website. Please try again.', 'assertive');
    }
  };

  useKeyboardShortcut(
    () => {
      if (!isLoading && requirements.trim()) {
        handleSubmit(handleFormSubmit)();
      }
    },
    {
      key: 's',
      ctrlKey: true,
      enabled: !isLoading,
    }
  );

  const charCount = requirements.length;
  const isValid = requirements.trim().length >= 10;

  return (
    <div className={cn('w-full', className)}>
      <div className="max-w-3xl mx-auto">
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-12">
          {/* Header */}
          <div className="space-y-4">
            <h1 className="text-4xl md:text-5xl font-semibold tracking-tight break-words">
              Build your website
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground break-words">
              Describe what you want to create, and AI will generate it for you.
            </p>
          </div>

          {/* Main Input */}
          <div className="space-y-4">
            <Textarea
              id="requirements"
              placeholder="I want to build a portfolio website with a hero section, project showcase, and contact form. The design should be modern and minimal with smooth animations..."
              className={cn(
                'min-h-[200px] resize-none text-lg leading-relaxed',
                'border-0 border-b-2 rounded-none px-0 py-4',
                'focus-visible:ring-0 focus-visible:border-foreground',
                'placeholder:text-muted-foreground/40',
                'transition-colors duration-200',
                errors.requirements && 'border-destructive'
              )}
              {...register('requirements')}
              disabled={isLoading}
            />
            <div className="flex items-center justify-between text-sm">
              <div>
                {errors.requirements ? (
                  <span className="text-destructive">{errors.requirements.message}</span>
                ) : (
                  <span className="text-muted-foreground">
                    {charCount === 0 ? 'Start typing...' : `${charCount} characters`}
                  </span>
                )}
              </div>
              {charCount > 0 && (
                <span className={cn(
                  'text-xs',
                  isValid ? 'text-green-600 dark:text-green-500' : 'text-muted-foreground'
                )}>
                  {isValid ? '✓ Ready' : `${10 - charCount} more needed`}
                </span>
              )}
            </div>
          </div>

          {/* Options Grid */}
          <div className="space-y-8">
            {/* Framework */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                Framework
              </label>
              <div className="flex flex-wrap gap-2">
                {frameworks.map((fw) => (
                  <button
                    key={fw.id}
                    type="button"
                    onClick={() => setValue('framework', fw.id as any)}
                    className={cn(
                      'px-4 py-2 text-sm font-medium rounded-full transition-all duration-200',
                      selectedFramework === fw.id
                        ? 'bg-foreground text-background'
                        : 'bg-muted/50 text-foreground hover:bg-muted'
                    )}
                    disabled={isLoading}
                  >
                    {fw.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Design Style */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                Style
              </label>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
                {designStyles.map((style) => (
                  <button
                    key={style.id}
                    type="button"
                    onClick={() => setValue('designStyle', style.id as any)}
                    className={cn(
                      'px-3 py-2 text-xs md:text-sm font-medium rounded-full transition-all duration-200 whitespace-nowrap',
                      selectedDesignStyle === style.id
                        ? 'bg-foreground text-background'
                        : 'bg-muted/50 text-foreground hover:bg-muted'
                    )}
                    disabled={isLoading}
                  >
                    {style.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Features */}
            <div className="space-y-3">
              <label className="text-sm font-medium text-muted-foreground uppercase tracking-wide">
                Features <span className="text-xs normal-case">(Optional)</span>
              </label>
              <div className="flex flex-wrap gap-2">
                {features.map((feature) => {
                  const isSelected = selectedFeatures.includes(feature.id);
                  return (
                    <button
                      key={feature.id}
                      type="button"
                      onClick={() => {
                        const updated = isSelected
                          ? selectedFeatures.filter((id) => id !== feature.id)
                          : [...selectedFeatures, feature.id];
                        setValue('features', updated);
                      }}
                      className={cn(
                        'px-4 py-2 text-sm font-medium rounded-full transition-all duration-200',
                        isSelected
                          ? 'bg-foreground text-background'
                          : 'bg-muted/50 text-foreground hover:bg-muted'
                      )}
                      disabled={isLoading}
                    >
                      {feature.name}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Color Scheme */}
            <div className="space-y-3">
              <label 
                htmlFor="colorScheme" 
                className="text-sm font-medium text-muted-foreground uppercase tracking-wide"
              >
                Color Preferences <span className="text-xs normal-case">(Optional)</span>
              </label>
              <input
                id="colorScheme"
                type="text"
                placeholder="e.g., blue and white, dark theme, warm tones..."
                className={cn(
                  'w-full bg-transparent text-base',
                  'border-0 border-b border-border px-0 py-3',
                  'focus:outline-none focus:border-foreground',
                  'placeholder:text-muted-foreground/40',
                  'transition-colors duration-200'
                )}
                {...register('colorScheme')}
                disabled={isLoading}
              />
            </div>
          </div>

          {/* Submit */}
          <div className="flex items-center justify-between pt-8 border-t">
            <div className="text-sm text-muted-foreground">
              <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">⌘</kbd>
              {' + '}
              <kbd className="px-2 py-1 bg-muted rounded text-xs font-mono">S</kbd>
              {' to generate'}
            </div>
            <Button
              type="submit"
              size="lg"
              disabled={isLoading || !isValid}
              className={cn(
                'group relative overflow-hidden',
                'bg-foreground text-background hover:bg-foreground/90',
                'h-12 px-8 text-base font-medium',
                'transition-all duration-200'
              )}
            >
              <span className="relative z-10 flex items-center gap-2">
                {isLoading ? (
                  <>
                    <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                    Generating
                  </>
                ) : (
                  <>
                    Generate
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                  </>
                )}
              </span>
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
