import { Theme } from '@/lib/types/theme';
import { ThemeCard } from './ThemeCard';

interface ThemeGridProps {
  themes: Theme[];
  selectedThemeId?: string;
  onPreview: (theme: Theme) => void;
  onSelect: (theme: Theme) => void;
}

export function ThemeGrid({ themes, selectedThemeId, onPreview, onSelect }: ThemeGridProps) {
  if (themes.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <p className="text-muted-foreground text-lg">No themes found</p>
        <p className="text-sm text-muted-foreground mt-2">Try adjusting your filters</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      {themes.map((theme) => (
        <ThemeCard
          key={theme.id}
          theme={theme}
          isSelected={theme.id === selectedThemeId}
          onPreview={onPreview}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
