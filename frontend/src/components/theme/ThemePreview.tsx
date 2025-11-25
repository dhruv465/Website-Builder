import { Theme } from '@/lib/types/theme';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { X } from 'lucide-react';

interface ThemePreviewProps {
  theme: Theme | null;
  isOpen: boolean;
  onClose: () => void;
  onApply: (theme: Theme) => void;
}

export function ThemePreview({ theme, isOpen, onClose, onApply }: ThemePreviewProps) {
  if (!theme) return null;

  const handleApply = () => {
    onApply(theme);
    onClose();
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-6xl h-[90vh] p-0">
        <DialogHeader className="p-6 pb-4">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <DialogTitle className="text-2xl">{theme.name}</DialogTitle>
              <DialogDescription className="mt-2">{theme.description}</DialogDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          <div className="flex flex-wrap gap-2 mt-4">
            <Badge variant="secondary">{theme.category}</Badge>
            {theme.tags.map((tag) => (
              <Badge key={tag} variant="outline">
                {tag}
              </Badge>
            ))}
          </div>
        </DialogHeader>

        <Separator />

        <div className="flex-1 overflow-auto p-6">
          <div className="space-y-6">
            {/* Color Palette */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Color Palette</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                {Object.entries(theme.colors).map(([name, color]) => (
                  <div key={name} className="space-y-2">
                    <div
                      className="w-full h-20 rounded-lg border-2 shadow-sm"
                      style={{ backgroundColor: color }}
                    />
                    <div className="text-sm">
                      <p className="font-medium capitalize">{name.replace(/([A-Z])/g, ' $1').trim()}</p>
                      <p className="text-xs text-muted-foreground font-mono">{color}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Separator />

            {/* Typography */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Typography</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Heading Font</p>
                  <p className="text-2xl font-bold" style={{ fontFamily: theme.fonts.heading }}>
                    {theme.fonts.heading}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Body Font</p>
                  <p className="text-lg" style={{ fontFamily: theme.fonts.body }}>
                    {theme.fonts.body}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-2">Monospace Font</p>
                  <p className="text-sm font-mono" style={{ fontFamily: theme.fonts.mono }}>
                    {theme.fonts.mono}
                  </p>
                </div>
              </div>
            </div>

            <Separator />

            {/* Preview Image */}
            <div>
              <h3 className="text-lg font-semibold mb-3">Full Preview</h3>
              <div className="aspect-video rounded-lg overflow-hidden border-2 shadow-lg">
                <img
                  src={theme.thumbnail_url}
                  alt={`${theme.name} full preview`}
                  className="w-full h-full object-cover"
                />
              </div>
            </div>
          </div>
        </div>

        <Separator />

        <div className="p-6 pt-4 flex justify-end gap-3">
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button onClick={handleApply}>Apply Theme</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
