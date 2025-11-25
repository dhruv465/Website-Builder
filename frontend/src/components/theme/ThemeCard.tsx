import { Theme } from '@/lib/types/theme';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Eye, Check } from 'lucide-react';

interface ThemeCardProps {
  theme: Theme;
  isSelected?: boolean;
  onPreview: (theme: Theme) => void;
  onSelect: (theme: Theme) => void;
}

export function ThemeCard({ theme, isSelected, onPreview, onSelect }: ThemeCardProps) {
  return (
    <Card className={`overflow-hidden transition-all hover:shadow-lg ${isSelected ? 'ring-2 ring-primary' : ''}`}>
      <div className="relative aspect-video overflow-hidden bg-muted">
        <img
          src={theme.thumbnail_url}
          alt={`${theme.name} preview`}
          className="w-full h-full object-cover"
          loading="lazy"
        />
        {isSelected && (
          <div className="absolute top-2 right-2 bg-primary text-primary-foreground rounded-full p-1">
            <Check className="w-4 h-4" />
          </div>
        )}
      </div>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-lg truncate">{theme.name}</CardTitle>
            <CardDescription className="line-clamp-2 mt-1">{theme.description}</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex flex-wrap gap-1">
          <Badge variant="secondary" className="text-xs">
            {theme.category}
          </Badge>
          {theme.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" className="text-xs">
              {tag}
            </Badge>
          ))}
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => onPreview(theme)}
          >
            <Eye className="w-4 h-4 mr-1" />
            Preview
          </Button>
          <Button
            variant={isSelected ? 'secondary' : 'default'}
            size="sm"
            className="flex-1"
            onClick={() => onSelect(theme)}
          >
            {isSelected ? 'Selected' : 'Select'}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
