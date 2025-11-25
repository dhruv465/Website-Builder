import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NaturalLanguageInput } from '../editor/NaturalLanguageInput';
import { apiClient } from '@/lib/api/client';
import { toast } from 'sonner';

// Mock dependencies
vi.mock('@/lib/api/client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}));

vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

describe('NaturalLanguageInput', () => {
  const mockOnApplyEdit = vi.fn();
  const defaultProps = {
    onApplyEdit: mockOnApplyEdit,
    htmlCode: '<div>Hello</div>',
    cssCode: '.test { color: red; }',
    selectedElement: '',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<NaturalLanguageInput {...defaultProps} />);
    expect(screen.getByPlaceholderText(/Describe your change/i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeInTheDocument();
  });

  it('updates input value when typing', () => {
    render(<NaturalLanguageInput {...defaultProps} />);
    const input = screen.getByPlaceholderText(/Describe your change/i);
    fireEvent.change(input, { target: { value: 'Make it blue' } });
    expect(input).toHaveValue('Make it blue');
  });

  it('disables button when input is empty', () => {
    render(<NaturalLanguageInput {...defaultProps} />);
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });

  it('handles successful edit submission', async () => {
    // Mock API responses
    (apiClient.post as any)
      .mockResolvedValueOnce({ data: { type: 'style', target: 'div', value: 'blue' } }) // parse
      .mockResolvedValueOnce({ 
        data: { 
          success: true, 
          html_code: '<div>Hello</div>', 
          css_code: '.test { color: blue; }',
          message: 'Updated style'
        } 
      }); // apply

    render(<NaturalLanguageInput {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/Describe your change/i);
    fireEvent.change(input, { target: { value: 'Make it blue' } });
    
    const button = screen.getByRole('button');
    fireEvent.click(button);

    // Check loading state
    expect(button).toBeDisabled();
    expect(screen.getByRole('button').querySelector('.animate-spin')).toBeInTheDocument();

    await waitFor(() => {
      expect(apiClient.post).toHaveBeenCalledTimes(2);
      expect(mockOnApplyEdit).toHaveBeenCalledWith('<div>Hello</div>', '.test { color: blue; }');
      expect(toast.success).toHaveBeenCalledWith('Updated style');
    });
  });

  it('handles API error during parsing', async () => {
    (apiClient.post as any).mockRejectedValueOnce(new Error('API Error'));

    render(<NaturalLanguageInput {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/Describe your change/i);
    fireEvent.change(input, { target: { value: 'Make it blue' } });
    
    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Failed to process your request.');
      expect(mockOnApplyEdit).not.toHaveBeenCalled();
    });
  });

  it('handles failed application of edit', async () => {
    (apiClient.post as any)
      .mockResolvedValueOnce({ data: { type: 'style' } }) // parse
      .mockResolvedValueOnce({ 
        data: { 
          success: false, 
          message: 'Could not apply edit'
        } 
      }); // apply

    render(<NaturalLanguageInput {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/Describe your change/i);
    fireEvent.change(input, { target: { value: 'Invalid command' } });
    
    const button = screen.getByRole('button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Could not apply edit');
      expect(mockOnApplyEdit).not.toHaveBeenCalled();
    });
  });
});
