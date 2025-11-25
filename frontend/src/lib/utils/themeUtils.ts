import { Theme, ColorPalette } from '../types/theme';

/**
 * Generate CSS variables from theme colors
 */
export function generateThemeVariables(colors: ColorPalette): string {
  return `
    --color-primary: ${colors.primary};
    --color-secondary: ${colors.secondary};
    --color-accent: ${colors.accent};
    --color-background: ${colors.background};
    --color-foreground: ${colors.foreground};
    --color-muted: ${colors.muted};
    --color-muted-foreground: ${colors.mutedForeground};
    --color-border: ${colors.border};
    --color-card: ${colors.card};
    --color-card-foreground: ${colors.cardForeground};
  `.trim();
}

/**
 * Generate complete CSS for theme application
 */
export function generateThemeCSS(theme: Theme): string {
  const cssVariables = generateThemeVariables(theme.colors);
  
  return `
:root {
  ${cssVariables}
}

body {
  font-family: ${theme.fonts.body};
  background-color: ${theme.colors.background};
  color: ${theme.colors.foreground};
}

h1, h2, h3, h4, h5, h6 {
  font-family: ${theme.fonts.heading};
}

code, pre {
  font-family: ${theme.fonts.mono};
}
  `.trim();
}

/**
 * Inject theme into an iframe
 */
export function injectThemeIntoIframe(iframe: HTMLIFrameElement, theme: Theme): void {
  const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
  if (!iframeDoc) return;

  // Remove existing theme style if present
  const existingStyle = iframeDoc.getElementById('theme-styles');
  if (existingStyle) {
    existingStyle.remove();
  }

  // Create and inject new theme style
  const styleElement = iframeDoc.createElement('style');
  styleElement.id = 'theme-styles';
  styleElement.textContent = generateThemeCSS(theme);
  iframeDoc.head.appendChild(styleElement);
}

/**
 * Apply theme to current document
 */
export function applyThemeToDocument(theme: Theme): void {
  const root = document.documentElement;
  
  // Apply CSS variables
  Object.entries(theme.colors).forEach(([key, value]) => {
    const cssVarName = `--color-${key.replace(/([A-Z])/g, '-$1').toLowerCase()}`;
    root.style.setProperty(cssVarName, value);
  });

  // Apply fonts
  root.style.setProperty('--font-heading', theme.fonts.heading);
  root.style.setProperty('--font-body', theme.fonts.body);
  root.style.setProperty('--font-mono', theme.fonts.mono);
}

/**
 * Convert hex color to RGB values
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } | null {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  if (!result || !result[1] || !result[2] || !result[3]) {
    return null;
  }
  return {
    r: parseInt(result[1], 16),
    g: parseInt(result[2], 16),
    b: parseInt(result[3], 16),
  };
}

/**
 * Calculate contrast ratio between two colors
 */
export function getContrastRatio(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);
  
  if (!rgb1 || !rgb2) return 0;

  const luminance = (rgb: { r: number; g: number; b: number }): number => {
    const normalize = (val: number): number => {
      const normalized = val / 255;
      return normalized <= 0.03928
        ? normalized / 12.92
        : Math.pow((normalized + 0.055) / 1.055, 2.4);
    };
    
    const r = normalize(rgb.r);
    const g = normalize(rgb.g);
    const b = normalize(rgb.b);
    
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  };

  const lum1 = luminance(rgb1);
  const lum2 = luminance(rgb2);
  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
}

/**
 * Check if theme meets WCAG AA contrast requirements
 */
export function validateThemeAccessibility(theme: Theme): {
  isValid: boolean;
  issues: string[];
} {
  const issues: string[] = [];
  
  // Check primary text contrast
  const primaryContrast = getContrastRatio(theme.colors.foreground, theme.colors.background);
  if (primaryContrast < 4.5) {
    issues.push(`Foreground/Background contrast ratio (${primaryContrast.toFixed(2)}) is below WCAG AA standard (4.5:1)`);
  }

  // Check card text contrast
  const cardContrast = getContrastRatio(theme.colors.cardForeground, theme.colors.card);
  if (cardContrast < 4.5) {
    issues.push(`Card text contrast ratio (${cardContrast.toFixed(2)}) is below WCAG AA standard (4.5:1)`);
  }

  return {
    isValid: issues.length === 0,
    issues,
  };
}
