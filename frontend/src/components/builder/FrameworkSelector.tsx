import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { Framework, FrameworkOption } from '@/lib/types/builder';

interface FrameworkSelectorProps {
  selected?: Framework;
  onSelect: (framework: Framework) => void;
  className?: string;
}

const frameworkOptions: FrameworkOption[] = [
  {
    id: 'react',
    name: 'React',
    description: 'Modern component-based library',
    icon: '⚛️',
  },
  {
    id: 'vue',
    name: 'Vue.js',
    description: 'Progressive JavaScript framework',
    icon: '💚',
  },
  {
    id: 'nextjs',
    name: 'Next.js',
    description: 'React framework with SSR',
    icon: '▲',
  },
  {
    id: 'html',
    name: 'HTML/CSS/JS',
    description: 'Pure vanilla web technologies',
    icon: '🌐',
  },
];

export const FrameworkSelector: React.FC<FrameworkSelectorProps> = ({
  selected,
  onSelect,
  className,
}) => {
  return (
    <div className={cn('grid grid-cols-1 md:grid-cols-2 gap-4', className)}>
      {frameworkOptions.map((framework) => {
        const isSelected = selected === framework.id;
        
        return (
          <Card
            key={framework.id}
            className={cn(
              'cursor-pointer transition-all hover:shadow-md',
              isSelected && 'ring-2 ring-primary border-primary'
            )}
            onClick={() => onSelect(framework.id)}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                onSelect(framework.id);
              }
            }}
            aria-pressed={isSelected}
          >
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-3xl" role="img" aria-label={framework.name}>
                    {framework.icon}
                  </span>
                  <CardTitle className="text-lg">{framework.name}</CardTitle>
                </div>
                {isSelected && <Badge>Selected</Badge>}
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription>{framework.description}</CardDescription>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
};
