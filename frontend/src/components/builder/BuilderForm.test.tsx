import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BuilderForm } from './BuilderForm';
import { BuilderFormData } from '@/lib/types/site';

describe('BuilderForm', () => {
  const mockOnSubmit = vi.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
    localStorage.clear();
  });

  it('renders form with all input fields', () => {
    render(<BuilderForm onSubmit={mockOnSubmit} />);

    expect(screen.getByText('Build your website')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/I want to build a portfolio/i)).toBeInTheDocument();
    expect(screen.getByText('Framework')).toBeInTheDocument();
    expect(screen.getByText('Style')).toBeInTheDocument();
    expect(screen.getByText('Features')).toBeInTheDocument();
  });

  it('displays character count for requirements input', async () => {
    const user = userEvent.setup();
    render(<BuilderForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByPlaceholderText(/I want to build a portfolio/i);
    await user.type(textarea, 'Test input');

    expect(screen.getByText(/10 characters/i)).toBeInTheDocument();
  });

  it('disables submit button for short requirements', async () => {
    const user = userEvent.setup();
    render(<BuilderForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByPlaceholderText(/I want to build a portfolio/i);
    await user.type(textarea, 'Short');

    const submitButton = screen.getByRole('button', { name: /generate/i });
    
    // Button should be disabled for short input
    expect(submitButton).toBeDisabled();
  });

  it('allows framework selection', async () => {
    const user = userEvent.setup();
    render(<BuilderForm onSubmit={mockOnSubmit} />);

    const reactButton = screen.getByRole('button', { name: 'React' });
    await user.click(reactButton);

    expect(reactButton).toHaveClass('bg-foreground');
  });

  it('allows design style selection', async () => {
    const user = userEvent.setup();
    render(<BuilderForm onSubmit={mockOnSubmit} />);

    const modernButton = screen.getByRole('button', { name: 'Modern' });
    await user.click(modernButton);

    expect(modernButton).toHaveClass('bg-foreground');
  });

  it('allows multiple feature selection', async () => {
    const user = userEvent.setup();
    render(<BuilderForm onSubmit={mockOnSubmit} />);

    const contactFormButton = screen.getByRole('button', { name: 'Contact Form' });
    const blogButton = screen.getByRole('button', { name: 'Blog' });

    await user.click(contactFormButton);
    await user.click(blogButton);

    expect(contactFormButton).toHaveClass('bg-foreground');
    expect(blogButton).toHaveClass('bg-foreground');
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    mockOnSubmit.mockResolvedValue(undefined);

    render(<BuilderForm onSubmit={mockOnSubmit} />);

    const textarea = screen.getByPlaceholderText(/I want to build a portfolio/i);
    await user.type(textarea, 'I want to build a modern portfolio website');

    const submitButton = screen.getByRole('button', { name: /generate/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          requirements: 'I want to build a modern portfolio website',
        })
      );
    });
  });

  it('disables submit button when loading', () => {
    render(<BuilderForm onSubmit={mockOnSubmit} isLoading={true} />);

    const submitButton = screen.getByRole('button', { name: /generating/i });
    expect(submitButton).toBeDisabled();
  });

  it('loads initial data when provided', () => {
    const initialData: Partial<BuilderFormData> = {
      requirements: 'Test requirements',
      framework: 'react',
      designStyle: 'modern',
    };

    render(<BuilderForm onSubmit={mockOnSubmit} initialData={initialData} />);

    const textarea = screen.getByPlaceholderText(/I want to build a portfolio/i);
    expect(textarea).toHaveValue('Test requirements');

    const reactButton = screen.getByRole('button', { name: 'React' });
    expect(reactButton).toHaveClass('bg-foreground');
  });
});
