import { useState } from 'react';
import { Theme, ColorPalette, FontConfig } from '@/lib/types/theme';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Separator } from '@/components/ui/separator';
import { ColorPicker } from './ColorPicker';
import { ScrollArea } from '@/components/ui/scroll-area';

interface ThemeCustomizerProps {
  theme: Theme | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (customizedTheme: Theme) => void;
}

export function ThemeCustomizer({ theme, isOpen, onClose, onSave }: ThemeCustomizerProps) {
  const [customColors, setCustomColors] = useState<ColorPalette | null>(null);
  const [customFonts, setCustomFonts] = useState<FontConfig | null>(null);

  if (!theme) return null;

  const colors = customColors || theme.colors;
  const fonts = customFonts || theme.fonts;

  const handleColorChange = (key: keyof ColorPalette, value: string) => {
    setCustomColors({
      ...(customColors || theme.colors),
      [key]: value,
    });
  };

  const handleFontChange = (key: keyof FontConfig, value: string) => {
    setCustomFonts({
      ...(customFonts || theme.fonts),
      [key]: value,
    });
  };

  const handleSave = () => {
    const customizedTheme: Theme = {
      ...theme,
      id: `${theme.id}-custom-${Date.now()}`,
      name: `${theme.name} (Custom)`,
      colors: customColors || theme.colors,
      fonts: customFonts || theme.fonts,
    };
    onSave(customizedTheme);
    onClose();
  };

  const handleReset = () => {
    setCustomColors(null);
    setCustomFonts(null);
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-3xl h-[90vh] p-0">
        <DialogHeader className="p-6 pb-4">
          <DialogTitle className="text-2xl">Customize Theme</DialogTitle>
          <DialogDescription>
            Customize colors and fonts for {theme.name}
          </DialogDescription>
        </DialogHeader>

        <Separator />

        <ScrollArea className="flex-1 px-6">
          <Tabs defaultValue="colors" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="colors">Colors</TabsTrigger>
              <TabsTrigger value="fonts">Fonts</TabsTrigger>
            </TabsList>

            <TabsContent value="colors" className="space-y-4 py-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <ColorPicker
                  label="Primary"
                  color={colors.primary}
                  onChange={(value) => handleColorChange('primary', value)}
                />
                <ColorPicker
                  label="Secondary"
                  color={colors.secondary}
                  onChange={(value) => handleColorChange('secondary', value)}
                />
                <ColorPicker
                  label="Accent"
                  color={colors.accent}
                  onChange={(value) => handleColorChange('accent', value)}
                />
                <ColorPicker
                  label="Background"
                  color={colors.background}
                  onChange={(value) => handleColorChange('background', value)}
                />
                <ColorPicker
                  label="Foreground"
                  color={colors.foreground}
                  onChange={(value) => handleColorChange('foreground', value)}
                />
                <ColorPicker
                  label="Muted"
                  color={colors.muted}
                  onChange={(value) => handleColorChange('muted', value)}
                />
                <ColorPicker
                  label="Muted Foreground"
                  color={colors.mutedForeground}
                  onChange={(value) => handleColorChange('mutedForeground', value)}
                />
                <ColorPicker
                  label="Border"
                  color={colors.border}
                  onChange={(value) => handleColorChange('border', value)}
                />
                <ColorPicker
                  label="Card"
                  color={colors.card}
                  onChange={(value) => handleColorChange('card', value)}
                />
                <ColorPicker
                  label="Card Foreground"
                  color={colors.cardForeground}
                  onChange={(value) => handleColorChange('cardForeground', value)}
                />
              </div>
            </TabsContent>

            <TabsContent value="fonts" className="space-y-4 py-4">
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="heading-font">Heading Font</Label>
                  <Input
                    id="heading-font"
                    type="text"
                    value={fonts.heading}
                    onChange={(e) => handleFontChange('heading', e.target.value)}
                    placeholder="e.g., Inter, sans-serif"
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter a font family name with fallbacks
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="body-font">Body Font</Label>
                  <Input
                    id="body-font"
                    type="text"
                    value={fonts.body}
                    onChange={(e) => handleFontChange('body', e.target.value)}
                    placeholder="e.g., Inter, sans-serif"
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter a font family name with fallbacks
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="mono-font">Monospace Font</Label>
                  <Input
                    id="mono-font"
                    type="text"
                    value={fonts.mono}
                    onChange={(e) => handleFontChange('mono', e.target.value)}
                    placeholder="e.g., JetBrains Mono, monospace"
                  />
                  <p className="text-sm text-muted-foreground">
                    Enter a font family name with fallbacks
                  </p>
                </div>

                <Separator className="my-6" />

                <div className="space-y-4">
                  <h4 className="font-semibold">Preview</h4>
                  <div className="space-y-3 p-4 border rounded-lg">
                    <p className="text-2xl font-bold" style={{ fontFamily: fonts.heading }}>
                      Heading Preview
                    </p>
                    <p className="text-base" style={{ fontFamily: fonts.body }}>
                      Body text preview with the selected font family.
                    </p>
                    <p className="text-sm font-mono" style={{ fontFamily: fonts.mono }}>
                      Monospace code preview
                    </p>
                  </div>
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </ScrollArea>

        <Separator />

        <div className="p-6 pt-4 flex justify-between">
          <Button variant="outline" onClick={handleReset}>
            Reset to Default
          </Button>
          <div className="flex gap-3">
            <Button variant="outline" onClick={onClose}>
              Cancel
            </Button>
            <Button onClick={handleSave}>Save Customization</Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
