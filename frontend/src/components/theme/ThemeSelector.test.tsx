import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeSelector } from './ThemeSelector';
import { Theme } from '@/lib/types/theme';

// Mock child components
vi.mock('./ThemeGrid', () => ({
  ThemeGrid: ({ themes, onSelect }: any) => (
    <div data-testid="theme-grid">
      {themes.map((theme: Theme) => (
        <button key={theme.id} onClick={() => onSelect(theme)}>
          {theme.name}
        </button>
      ))}
    </div>
  ),
}));

vi.mock('./ThemePreview', () => ({
  ThemePreview: ({ theme, isOpen, onClose, onApply }: any) =>
    isOpen ? (
      <div data-testid="theme-preview">
        <span>{theme?.name}</span>
        <button onClick={onClose}>Close</button>
        <button onClick={() => onApply(theme)}>Apply</button>
      </div>
    ) : null,
}));

vi.mock('./ThemeCustomizer', () => ({
  ThemeCustomizer: ({ theme, isOpen, onClose, onSave }: any) =>
    isOpen ? (
      <div data-testid="theme-customizer">
        <span>{theme?.name}</span>
        <button onClick={onClose}>Close</button>
        <button onClick={() => onSave(theme)}>Save</button>
      </div>
    ) : null,
}));

describe('ThemeSelector', () => {
  const mockThemes: Theme[] = [
    {
      id: 'theme-1',
      name: 'Modern Blue',
      description: 'A modern blue theme',
      category: 'modern',
      thumbnail_url: '/thumb1.jpg',
      preview_url: '/preview1.jpg',
      colors: {
        primary: '#0066cc',
        secondary: '#00aaff',
        accent: '#ff6600',
        background: '#ffffff',
        foreground: '#000000',
      },
      fonts: {
        heading: 'Inter',
        body: 'Inter',
      },
      spacing: {
        base: 16,
        scale: 1.5,
      },
      tags: ['professional', 'clean'],
      popularity: 100,
    },
    {
      id: 'theme-2',
      name: 'Minimal Dark',
      description: 'A minimal dark theme',
      category: 'minimal',
      thumbnail_url: '/thumb2.jpg',
      preview_url: '/preview2.jpg',
      colors: {
        primary: '#ffffff',
        secondary: '#cccccc',
        accent: '#ff0000',
        background: '#000000',
        foreground: '#ffffff',
      },
      fonts: {
        heading: 'Roboto',
        body: 'Roboto',
      },
      spacing: {
        base: 16,
        scale: 1.5,
      },
      tags: ['dark', 'simple'],
      popularity: 90,
    },
  ];

  const mockOnThemeSelect = vi.fn();
  const mockOnThemeApply = vi.fn();

  beforeEach(() => {
    mockOnThemeSelect.mockClear();
    mockOnThemeApply.mockClear();
  });

  it('renders theme selector with header', () => {
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    expect(screen.getByText('Theme Gallery')).toBeInTheDocument();
    expect(screen.getByText(/2 professionally designed themes/i)).toBeInTheDocument();
  });

  it('displays search input', () => {
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    expect(screen.getByPlaceholderText(/search themes/i)).toBeInTheDocument();
  });

  it('filters themes by search query', async () => {
    const user = userEvent.setup();
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    const searchInput = screen.getByPlaceholderText(/search themes/i);
    await user.type(searchInput, 'Modern');

    await waitFor(() => {
      expect(screen.getByText('1 theme found')).toBeInTheDocument();
    });
  });

  it('displays category filter tabs', () => {
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    expect(screen.getByRole('tab', { name: 'all' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'modern' })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: 'minimal' })).toBeInTheDocument();
  });

  it('filters themes by category', async () => {
    const user = userEvent.setup();
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    const modernTab = screen.getByRole('tab', { name: 'modern' });
    await user.click(modernTab);

    await waitFor(() => {
      expect(screen.getByText('1 theme found')).toBeInTheDocument();
    });
  });

  it('toggles between grid and list view', async () => {
    const user = userEvent.setup();
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    const listViewButton = screen.getByLabelText('List view');
    await user.click(listViewButton);

    // In list view, themes should still be displayed
    expect(screen.getByText('Modern Blue')).toBeInTheDocument();
  });

  it('calls onThemeSelect when theme is selected', async () => {
    const user = userEvent.setup();
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    const themeButton = screen.getByRole('button', { name: 'Modern Blue' });
    await user.click(themeButton);

    expect(mockOnThemeSelect).toHaveBeenCalledWith(mockThemes[0]);
  });

  it('displays results count', () => {
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    expect(screen.getByText('2 themes found')).toBeInTheDocument();
  });

  it('sorts themes by popularity', () => {
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    const themeButtons = screen.getAllByRole('button', { name: /Modern|Minimal/i });
    expect(themeButtons[0]).toHaveTextContent('Modern Blue');
  });

  it('filters by tags in search', async () => {
    const user = userEvent.setup();
    render(
      <ThemeSelector
        themes={mockThemes}
        onThemeSelect={mockOnThemeSelect}
      />
    );

    const searchInput = screen.getByPlaceholderText(/search themes/i);
    await user.type(searchInput, 'professional');

    await waitFor(() => {
      expect(screen.getByText('1 theme found')).toBeInTheDocument();
    });
  });

  it('shows customize button when theme is selected', () => {
    render(
      <ThemeSelector
        themes={mockThemes}
        selectedThemeId="theme-1"
        onThemeSelect={mockOnThemeSelect}
      />
    );

    expect(screen.getByRole('button', { name: /customize selected/i })).toBeInTheDocument();
  });
});
