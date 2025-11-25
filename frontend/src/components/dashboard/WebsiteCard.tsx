import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardFooter, CardHeader } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  MoreVertical, 
  Edit, 
  Rocket, 
  Trash2, 
  Copy, 
  Calendar
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Site } from '@/lib/types/api';
import { formatDistanceToNow } from 'date-fns';

interface WebsiteCardProps {
  site: Site;
  onDelete: (id: string) => void;
  onDuplicate: (id: string) => void;
}

export function WebsiteCard({ site, onDelete, onDuplicate }: WebsiteCardProps) {
  const navigate = useNavigate();

  return (
    <Card className="group hover:shadow-md transition-all duration-200 border-border/50 hover:border-border">
      <CardHeader className="p-0">
        <div 
          className="aspect-video w-full bg-muted/30 relative overflow-hidden rounded-t-lg cursor-pointer group-hover:bg-muted/50 transition-colors"
          onClick={() => navigate(`/builder/${site.id}`)}
        >
          {/* Placeholder for thumbnail - in real app would be an image */}
          <div className="absolute inset-0 flex items-center justify-center text-muted-foreground/20">
            <div className="w-16 h-16 rounded-full bg-background/50 flex items-center justify-center">
              <span className="text-2xl font-bold">{site.name.charAt(0)}</span>
            </div>
          </div>
          
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="secondary" size="icon" className="h-8 w-8" data-testid="website-card-menu">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem onClick={() => navigate(`/builder/${site.id}`)}>
                  <Edit className="mr-2 h-4 w-4" />
                  Edit
                </DropdownMenuItem>
                <DropdownMenuItem onClick={() => onDuplicate(site.id)}>
                  <Copy className="mr-2 h-4 w-4" />
                  Duplicate
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-destructive" onClick={() => onDelete(site.id)}>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-4">
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="font-semibold truncate pr-2" title={site.name}>
              {site.name}
            </h3>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <Calendar className="h-3 w-3" />
              Edited {formatDistanceToNow(new Date(site.updated_at), { addSuffix: true })}
            </p>
          </div>
          <Badge variant="outline" className="text-xs capitalize">
            {site.framework || 'React'}
          </Badge>
        </div>
      </CardContent>

      <CardFooter className="p-4 pt-0 flex gap-2">
        <Button 
          variant="outline" 
          size="sm" 
          className="flex-1"
          onClick={() => navigate(`/builder/${site.id}`)}
        >
          <Edit className="mr-2 h-3 w-3" />
          Edit
        </Button>
        <Button variant="default" size="sm" className="flex-1">
          <Rocket className="mr-2 h-3 w-3" />
          Deploy
        </Button>
      </CardFooter>
    </Card>
  );
}
