import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useSession } from '@/lib/context/SessionContext';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { WebsiteCard } from '@/components/dashboard/WebsiteCard';
import { Button } from '@/components/ui/button';
import { Plus } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { useAnnouncer } from '@/lib/hooks/useAnnouncer';

export default function DashboardPage() {
  const { session, refreshSession } = useSession();
  const navigate = useNavigate();
  const { announce } = useAnnouncer();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('newest');

  const filteredSites = useMemo(() => {
    if (!session?.sites) return [];
    
    let sites = [...session.sites];
    
    // Filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      sites = sites.filter(site => 
        site.name.toLowerCase().includes(query) || 
        site.framework?.toLowerCase().includes(query)
      );
    }
    
    // Sort
    sites.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
        case 'oldest':
          return new Date(a.updated_at).getTime() - new Date(b.updated_at).getTime();
        case 'name-asc':
          return a.name.localeCompare(b.name);
        case 'name-desc':
          return b.name.localeCompare(a.name);
        default:
          return 0;
      }
    });
    
    return sites;
  }, [session?.sites, searchQuery, sortBy]);

  const handleDelete = async (siteId: string) => {
    if (confirm('Are you sure you want to delete this website? This action cannot be undone.')) {
      try {
        await apiClient.delete(`/api/sites/${siteId}`);
        await refreshSession();
        announce('Website deleted successfully', 'polite');
      } catch (error) {
        console.error('Failed to delete site:', error);
        announce('Failed to delete website', 'assertive');
      }
    }
  };

  const handleDuplicate = async (siteId: string) => {
    // Implementation for duplicate would go here
    // For now just navigate to builder
    navigate(`/builder/${siteId}`);
  };

  const handleCreateNew = () => {
    navigate('/builder');
  };

  if (!session) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4 max-w-7xl">
      <DashboardHeader 
        onSearch={setSearchQuery}
        onSortChange={setSortBy}
        onCreateNew={handleCreateNew}
      />

      {filteredSites.length === 0 ? (
        <div className="text-center py-20 border-2 border-dashed rounded-lg bg-muted/30">
          <div className="mb-4">
            <div className="mx-auto w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <Plus className="h-8 w-8 text-primary" />
            </div>
          </div>
          <h3 className="text-xl font-semibold mb-2">No websites found</h3>
          <p className="text-muted-foreground mb-6 max-w-sm mx-auto">
            {searchQuery 
              ? "We couldn't find any websites matching your search." 
              : "You haven't created any websites yet. Start building your dream site today!"}
          </p>
          <Button onClick={handleCreateNew} size="lg">
            Create Your First Website
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredSites.map((site) => (
            <WebsiteCard 
              key={site.id} 
              site={site} 
              onDelete={handleDelete}
              onDuplicate={handleDuplicate}
            />
          ))}
        </div>
      )}
    </div>
  );
}
