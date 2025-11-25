import React from 'react';
import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';
import { FeatureOption } from '@/lib/types/builder';

interface FeatureCheckboxesProps {
  selected: string[];
  onToggle: (featureId: string) => void;
  className?: string;
}

const featureOptions: FeatureOption[] = [
  {
    id: 'contact-form',
    name: 'Contact Form',
    description: 'Add a contact form with validation',
  },
  {
    id: 'newsletter',
    name: 'Newsletter Signup',
    description: 'Email subscription form',
  },
  {
    id: 'blog',
    name: 'Blog Section',
    description: 'Blog posts with categories',
  },
  {
    id: 'gallery',
    name: 'Image Gallery',
    description: 'Photo gallery with lightbox',
  },
  {
    id: 'testimonials',
    name: 'Testimonials',
    description: 'Customer reviews section',
  },
  {
    id: 'pricing',
    name: 'Pricing Table',
    description: 'Product or service pricing',
  },
  {
    id: 'faq',
    name: 'FAQ Section',
    description: 'Frequently asked questions',
  },
  {
    id: 'social-links',
    name: 'Social Media Links',
    description: 'Links to social profiles',
  },
  {
    id: 'analytics',
    name: 'Analytics Integration',
    description: 'Google Analytics tracking',
  },
  {
    id: 'seo',
    name: 'SEO Optimization',
    description: 'Meta tags and structured data',
  },
];

export const FeatureCheckboxes: React.FC<FeatureCheckboxesProps> = ({
  selected,
  onToggle,
  className,
}) => {
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 gap-4', className)}>
      {featureOptions.map((feature) => {
        const isChecked = selected.includes(feature.id);
        
        return (
          <div
            key={feature.id}
            className="flex items-start space-x-3 p-3 rounded-lg border hover:bg-muted/50 transition-colors"
          >
            <Checkbox
              id={feature.id}
              checked={isChecked}
              onCheckedChange={() => onToggle(feature.id)}
              aria-describedby={`${feature.id}-description`}
            />
            <div className="flex-1 space-y-1">
              <Label
                htmlFor={feature.id}
                className="cursor-pointer font-medium leading-none"
              >
                {feature.name}
              </Label>
              <p
                id={`${feature.id}-description`}
                className="text-sm text-muted-foreground"
              >
                {feature.description}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
};
