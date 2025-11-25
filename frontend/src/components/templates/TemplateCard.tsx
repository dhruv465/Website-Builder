import { Card, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Eye, Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

interface TemplateCardProps {
  id: string;
  name: string;
  description: string;
  category: string;
  tags: string[];
  thumbnail_url: string;
  framework: string;
  onClick?: () => void;
  className?: string;
}

export function TemplateCard({
  name,
  description,
  tags,
  thumbnail_url,
  framework,
  onClick,
  className,
}: TemplateCardProps) {
  return (
    <Card
      className={cn(
        'group cursor-pointer hover:shadow-lg transition-all duration-300',
        className
      )}
      onClick={onClick}
    >
      <div className="relative aspect-video overflow-hidden rounded-t-lg bg-muted">
        {thumbnail_url.startsWith('http') ? (
          <img
            src={thumbnail_url}
            alt={name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            loading="lazy"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/10 to-primary/5">
            <Sparkles className="h-12 w-12 text-primary/40" />
          </div>
        )}
        <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors duration-300 flex items-center justify-center">
          <Button
            size="sm"
            className="opacity-0 group-hover:opacity-100 transition-opacity duration-300"
          >
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </Button>
        </div>
      </div>
      <CardHeader>
        <CardTitle className="text-lg">{name}</CardTitle>
        <CardDescription className="line-clamp-2">
          {description}
        </CardDescription>
      </CardHeader>
      <CardFooter className="flex flex-wrap gap-2">
        <Badge variant="secondary" className="text-xs">
          {framework}
        </Badge>
        {tags.slice(0, 2).map((tag) => (
          <Badge key={tag} variant="outline" className="text-xs">
            {tag}
          </Badge>
        ))}
      </CardFooter>
    </Card>
  );
}
