import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ChatProvider, useChatContext } from '../../src/context/ChatContext';

const TestComponent = () => {
  const context = useChatContext();
  return (
    <div>
      <span data-testid="status">{context.status}</span>
      <span data-testid="activeView">{context.activeView}</span>
    </div>
  );
};

describe('ChatProvider', () => {
  it('provides default values', () => {
    render(
      <ChatProvider>
        <TestComponent />
      </ChatProvider>
    );
    expect(screen.getByTestId('status')).toHaveTextContent('Backend ready at /api');
    expect(screen.getByTestId('activeView')).toHaveTextContent('home');
  });
});
