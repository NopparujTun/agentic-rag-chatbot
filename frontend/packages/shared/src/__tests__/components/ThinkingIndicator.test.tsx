import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { ThinkingIndicator } from '../../components/ThinkingIndicator';

describe('ThinkingIndicator', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders initial step when step prop is not provided', () => {
    render(<ThinkingIndicator />);
    expect(screen.getByText('Rewriting query...')).toBeInTheDocument();
    expect(screen.queryByText('Using tools...')).not.toBeInTheDocument();
  });

  it('advances internal step over time', () => {
    render(<ThinkingIndicator />);
    
    act(() => {
      vi.advanceTimersByTime(2000);
    });
    expect(screen.getByText('Using tools...')).toBeInTheDocument();
    
    act(() => {
      vi.advanceTimersByTime(8000); // 4 more steps
    });
    expect(screen.getByText('Generating answer...')).toBeInTheDocument();
  });

  it('uses provided step prop', () => {
    render(<ThinkingIndicator step={2} />);
    expect(screen.getByText('Rewriting query...')).toBeInTheDocument();
    expect(screen.getByText('Using tools...')).toBeInTheDocument();
    expect(screen.getByText('Searching knowledge base...')).toBeInTheDocument();
    expect(screen.queryByText('Reading documents...')).not.toBeInTheDocument();
  });

  it('caps the step properly', () => {
    render(<ThinkingIndicator step={100} />);
    expect(screen.getByText('Generating answer...')).toBeInTheDocument();
  });
});
