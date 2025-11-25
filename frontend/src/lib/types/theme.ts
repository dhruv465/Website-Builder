// Theme type definitions

export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  foreground: string;
  muted: string;
  mutedForeground: string;
  border: string;
  card: string;
  cardForeground: string;
}

export interface FontConfig {
  heading: string;
  body: string;
  mono: string;
}

export interface SpacingConfig {
  base: number;
  scale: number[];
}

export interface Theme {
  id: string;
  name: string;
  description: string;
  category: 'modern' | 'minimal' | 'corporate' | 'creative' | 'elegant' | 'bold';
  preview_url: string;
  thumbnail_url: string;
  colors: ColorPalette;
  fonts: FontConfig;
  spacing: SpacingConfig;
  tags: string[];
  popularity: number;
  created_at: string;
}

export interface ThemeCustomization {
  themeId: string;
  colors?: Partial<ColorPalette>;
  fonts?: Partial<FontConfig>;
  spacing?: Partial<SpacingConfig>;
}

export type ThemeViewMode = 'grid' | 'list';

export type ThemeCategory = Theme['category'] | 'all';
