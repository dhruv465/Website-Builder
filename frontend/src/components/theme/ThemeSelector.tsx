import { useState, useMemo } from 'react';
import { Theme, ThemeCategory, ThemeViewMode } from '@/lib/types/theme';
import { ThemeGrid } from './ThemeGrid';
import { ThemePreview } from './ThemePreview';
import { ThemeCustomizer } from './ThemeCustomizer';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Search, Grid3x3, List, Palette } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface ThemeSelectorProps {
  themes: Theme[];
  selectedThemeId?: string;
  onThemeSelect: (theme: Theme) => void;
  onThemeApply?: (theme: Theme) => void;
}

export function ThemeSelector({
  themes,
  selectedThemeId,
  onThemeSelect,
  onThemeApply,
}: ThemeSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<ThemeCategory>('all');
  const [viewMode, setViewMode] = useState<ThemeViewMode>('grid');
  const [previewTheme, setPreviewTheme] = useState<Theme | null>(null);
  const [customizeTheme, setCustomizeTheme] = useState<Theme | null>(null);

  // Filter themes based on search and category
  const filteredThemes = useMemo(() => {
    return themes.filter((theme) => {
      const matchesSearch =
        searchQuery === '' ||
        theme.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        theme.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        theme.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesCategory = selectedCategory === 'all' || theme.category === selectedCategory;

      return matchesSearch && matchesCategory;
    });
  }, [themes, searchQuery, selectedCategory]);

  // Sort by popularity
  const sortedThemes = useMemo(() => {
    return [...filteredThemes].sort((a, b) => b.popularity - a.popularity);
  }, [filteredThemes]);

  const categories: ThemeCategory[] = ['all', 'modern', 'minimal', 'corporate', 'creative', 'elegant', 'bold'];

  const handlePreview = (theme: Theme) => {
    setPreviewTheme(theme);
  };

  const handleApply = (theme: Theme) => {
    onThemeSelect(theme);
    if (onThemeApply) {
      onThemeApply(theme);
    }
  };

  const handleCustomize = (theme: Theme) => {
    setCustomizeTheme(theme);
  };

  const handleSaveCustomization = (customizedTheme: Theme) => {
    onThemeSelect(customizedTheme);
    if (onThemeApply) {
      onThemeApply(customizedTheme);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold">Theme Gallery</h2>
            <p className="text-muted-foreground mt-1">
              Choose from {themes.length} professionally designed themes
            </p>
          </div>
          <div className="flex gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('grid')}
              aria-label="Grid view"
            >
              <Grid3x3 className="w-4 h-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('list')}
              aria-label="List view"
            >
              <List className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            type="text"
            placeholder="Search themes by name, description, or tags..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Category Filters */}
        <Tabs value={selectedCategory} onValueChange={(value) => setSelectedCategory(value as ThemeCategory)}>
          <TabsList className="w-full justify-start overflow-x-auto">
            {categories.map((category) => (
              <TabsTrigger key={category} value={category} className="capitalize">
                {category}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      {/* Results Count */}
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {sortedThemes.length} {sortedThemes.length === 1 ? 'theme' : 'themes'} found
        </p>
        {selectedThemeId && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              const selected = themes.find((t) => t.id === selectedThemeId);
              if (selected) handleCustomize(selected);
            }}
          >
            <Palette className="w-4 h-4 mr-2" />
            Customize Selected
          </Button>
        )}
      </div>

      {/* Theme Grid */}
      {viewMode === 'grid' ? (
        <ThemeGrid
          themes={sortedThemes}
          selectedThemeId={selectedThemeId}
          onPreview={handlePreview}
          onSelect={handleApply}
        />
      ) : (
        <div className="space-y-4">
          {sortedThemes.map((theme) => (
            <Card key={theme.id} className="p-4">
              <div className="flex gap-4">
                <img
                  src={theme.thumbnail_url}
                  alt={theme.name}
                  className="w-32 h-24 object-cover rounded"
                />
                <div className="flex-1">
                  <h3 className="font-semibold">{theme.name}</h3>
                  <p className="text-sm text-muted-foreground">{theme.description}</p>
                </div>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={() => handlePreview(theme)}>
                    Preview
                  </Button>
                  <Button size="sm" onClick={() => handleApply(theme)}>
                    Select
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Preview Modal */}
      <ThemePreview
        theme={previewTheme}
        isOpen={!!previewTheme}
        onClose={() => setPreviewTheme(null)}
        onApply={handleApply}
      />

      {/* Customizer Modal */}
      <ThemeCustomizer
        theme={customizeTheme}
        isOpen={!!customizeTheme}
        onClose={() => setCustomizeTheme(null)}
        onSave={handleSaveCustomization}
      />
    </div>
  );
}
