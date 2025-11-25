import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { WebsiteCard } from '../dashboard/WebsiteCard';
import { Site } from '@/lib/types/api';

// Mock dependencies
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

vi.mock('date-fns', () => ({
  formatDistanceToNow: () => '2 days ago',
}));

describe('WebsiteCard', () => {
  const mockSite: Site = {
    id: 'site-123',
    name: 'My Awesome Site',
    description: 'A test site',
    framework: 'React',
    design_style: 'Modern',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-02T00:00:00Z',
    session_id: 'session-123',
    versions: [],
    audits: [],
    deployments: [],
  };

  const mockOnDelete = vi.fn();
  const mockOnDuplicate = vi.fn();

  it('renders site information correctly', () => {
    render(
      <WebsiteCard 
        site={mockSite} 
        onDelete={mockOnDelete} 
        onDuplicate={mockOnDuplicate} 
      />
    );

    expect(screen.getByText('My Awesome Site')).toBeInTheDocument();
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('Edited 2 days ago')).toBeInTheDocument();
  });

  it('navigates to builder on click', async () => {
    const user = userEvent.setup();
    render(
      <WebsiteCard 
        site={mockSite} 
        onDelete={mockOnDelete} 
        onDuplicate={mockOnDuplicate} 
      />
    );

    const editButton = screen.getByRole('button', { name: /edit/i });
    await user.click(editButton);

    expect(mockNavigate).toHaveBeenCalledWith('/builder/site-123');
  });

  it('calls onDuplicate when duplicate action is selected', async () => {
    const user = userEvent.setup();
    render(
      <WebsiteCard 
        site={mockSite} 
        onDelete={mockOnDelete} 
        onDuplicate={mockOnDuplicate} 
      />
    );

    // Open dropdown
    const menuButton = screen.getByTestId('website-card-menu');
    await user.click(menuButton);

    // Click duplicate
    const duplicateItem = await screen.findByText('Duplicate');
    await user.click(duplicateItem);

    expect(mockOnDuplicate).toHaveBeenCalledWith('site-123');
  });

  it('calls onDelete when delete action is selected', async () => {
    const user = userEvent.setup();
    render(
      <WebsiteCard 
        site={mockSite} 
        onDelete={mockOnDelete} 
        onDuplicate={mockOnDuplicate} 
      />
    );

    // Open dropdown
    const menuButton = screen.getByTestId('website-card-menu');
    await user.click(menuButton);

    // Click delete
    const deleteItem = await screen.findByText('Delete');
    await user.click(deleteItem);

    expect(mockOnDelete).toHaveBeenCalledWith('site-123');
  });
});
