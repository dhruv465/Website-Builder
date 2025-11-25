import { useState } from 'react';
import { ThemeSelector } from '@/components/theme';
import { useTheme } from '@/lib/hooks/useTheme';
import { Theme } from '@/lib/types/theme';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Palette } from 'lucide-react';

export function ThemeTestPage() {
  const { themes, selectedTheme, applyTheme } = useTheme();
  const [appliedTheme, setAppliedTheme] = useState<Theme | null>(null);

  const handleThemeSelect = (theme: Theme) => {
    setAppliedTheme(theme);
  };

  const handleThemeApply = async (theme: Theme) => {
    try {
      await applyTheme(theme);
      setAppliedTheme(theme);
    } catch (error) {
      console.error('Failed to apply theme:', error);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8 space-y-8">
        {/* Header */}
        <div className="space-y-2">
          <h1 className="text-4xl font-bold">Theme Selector Test Page</h1>
          <p className="text-muted-foreground">
            Test the theme selection and customization functionality
          </p>
        </div>

        <Separator />

        {/* Current Theme Display */}
        {(appliedTheme || selectedTheme) && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <Palette className="w-5 h-5" />
                <CardTitle>Currently Applied Theme</CardTitle>
              </div>
              <CardDescription>
                This theme is currently applied to the page
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex items-start gap-6">
                <img
                  src={(appliedTheme || selectedTheme)!.thumbnail_url}
                  alt={(appliedTheme || selectedTheme)!.name}
                  className="w-48 h-36 object-cover rounded-lg border-2"
                />
                <div className="flex-1 space-y-3">
                  <div>
                    <h3 className="text-2xl font-bold">{(appliedTheme || selectedTheme)!.name}</h3>
                    <p className="text-muted-foreground mt-1">
                      {(appliedTheme || selectedTheme)!.description}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary">
                      {(appliedTheme || selectedTheme)!.category}
                    </Badge>
                    {(appliedTheme || selectedTheme)!.tags.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex gap-4 pt-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Primary Color</p>
                      <div className="flex items-center gap-2 mt-1">
                        <div
                          className="w-8 h-8 rounded border-2"
                          style={{ backgroundColor: (appliedTheme || selectedTheme)!.colors.primary }}
                        />
                        <span className="font-mono text-sm">
                          {(appliedTheme || selectedTheme)!.colors.primary}
                        </span>
                      </div>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Heading Font</p>
                      <p className="mt-1 font-semibold">
                        {(appliedTheme || selectedTheme)!.fonts.heading.split(',')[0]}
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Demo Content */}
        <Card>
          <CardHeader>
            <CardTitle>Theme Preview Content</CardTitle>
            <CardDescription>
              This content demonstrates how the selected theme affects the page styling
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <h2 className="text-3xl font-bold mb-2">Heading Example</h2>
              <p className="text-muted-foreground">
                This is body text that demonstrates the theme's typography and color choices.
                The theme affects all aspects of the page including backgrounds, text colors,
                borders, and more.
              </p>
            </div>
            <div className="flex gap-2">
              <Button>Primary Button</Button>
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="outline">Outline Button</Button>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Card 1</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Card content example</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Card 2</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Card content example</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Card 3</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">Card content example</p>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>

        <Separator />

        {/* Theme Selector */}
        <ThemeSelector
          themes={themes}
          selectedThemeId={appliedTheme?.id || selectedTheme?.id}
          onThemeSelect={handleThemeSelect}
          onThemeApply={handleThemeApply}
        />
      </div>
    </div>
  );
}
