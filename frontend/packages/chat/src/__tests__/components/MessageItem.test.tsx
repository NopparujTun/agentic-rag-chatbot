import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MessageItem from '../../components/MessageItem';
import type { ChatMessage } from '@mfa/shared';

vi.mock('@mfa/shared', async (importOriginal) => {
  const actual = await importOriginal() as any;
  return {
    ...actual,
    useTypingEffect: (text: string) => ({ displayedText: text, isTyping: false }),
  };
});

describe('MessageItem', () => {
  it('renders user message', () => {
    const msg: ChatMessage = { id: 1, role: 'user', content: 'hello' };
    render(<MessageItem message={msg} isLatestAssistantMessage={false} />);
    expect(screen.getByText('hello')).toBeInTheDocument();
  });

  it('renders assistant message', () => {
    const msg: ChatMessage = { id: 2, role: 'assistant', content: 'assistant response' };
    render(<MessageItem message={msg} isLatestAssistantMessage={false} />);
    expect(screen.getByText('assistant response')).toBeInTheDocument();
  });

  it('renders system message', () => {
    const msg: ChatMessage = { id: 3, role: 'system', content: 'system note' };
    render(<MessageItem message={msg} isLatestAssistantMessage={false} />);
    expect(screen.getByText('system note')).toBeInTheDocument();
  });

  it('renders thinking indicator', () => {
    const msg: ChatMessage = { id: 4, role: 'assistant', content: '' };
    const { container } = render(<MessageItem message={msg} isLatestAssistantMessage={true} isThinking={true} />);
    // Testing thinking indicator is present
    expect(container.querySelector('.animate-spin')).toBeInTheDocument();
  });
});
