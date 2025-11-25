import { Search, Plus, Filter, SortAsc } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

interface DashboardHeaderProps {
  onSearch: (query: string) => void;
  onSortChange: (sort: string) => void;
  onCreateNew: () => void;
}

export function DashboardHeader({ onSearch, onSortChange, onCreateNew }: DashboardHeaderProps) {
  return (
    <div className="space-y-4 mb-8">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">My Websites</h1>
          <p className="text-muted-foreground mt-1">
            Manage and deploy your AI-generated projects.
          </p>
        </div>
        <Button onClick={onCreateNew} size="lg" className="w-full sm:w-auto gap-2">
          <Plus className="h-4 w-4" />
          Create New Website
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-center">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search websites..." 
            className="pl-9"
            onChange={(e) => onSearch(e.target.value)}
          />
        </div>
        
        <div className="flex gap-2 w-full sm:w-auto">
          <Select onValueChange={onSortChange} defaultValue="newest">
            <SelectTrigger className="w-[160px]">
              <div className="flex items-center gap-2">
                <SortAsc className="h-4 w-4 text-muted-foreground" />
                <SelectValue placeholder="Sort by" />
              </div>
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="newest">Newest First</SelectItem>
              <SelectItem value="oldest">Oldest First</SelectItem>
              <SelectItem value="name-asc">Name (A-Z)</SelectItem>
              <SelectItem value="name-desc">Name (Z-A)</SelectItem>
            </SelectContent>
          </Select>

          <Button variant="outline" size="icon">
            <Filter className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}
