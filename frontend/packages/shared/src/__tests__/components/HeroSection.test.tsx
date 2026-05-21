import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import HeroSection from '../../components/HeroSection';

describe('HeroSection', () => {
  it('renders default view without description', () => {
    render(<HeroSection />);
    expect(screen.getByText('How can I help you today?')).toBeInTheDocument();
    expect(screen.getByText('Available tools')).toBeInTheDocument();
    expect(screen.getByText('Summarize text')).toBeInTheDocument();
    expect(screen.queryByText(/This is an intelligent AI chatbot/i)).not.toBeInTheDocument();
  });

  it('renders with description when prop is true', () => {
    render(<HeroSection showDescription={true} />);
    expect(screen.getByText(/This is an intelligent AI chatbot/i)).toBeInTheDocument();
  });

  it('renders tool buttons with badges', () => {
    render(<HeroSection />);
    // "Analyze data" has a "NEW" badge
    const badge = screen.getByText('NEW');
    expect(badge).toBeInTheDocument();
  });
});
