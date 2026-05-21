import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import ChatSidebar from '../../components/ChatSidebar';

describe('ChatSidebar', () => {
  it('renders and allows searching chats', () => {
    const onNewChat = vi.fn();
    const onClear = vi.fn();
    const onCollapse = vi.fn();

    render(
      <ChatSidebar
        onNewChat={onNewChat}
        onClearKnowledgeBase={onClear}
        onCollapse={onCollapse}
      />
    );

    expect(screen.getByText('New Chat')).toBeInTheDocument();
    expect(screen.getByText('Analog Clock React app')).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText('Search');
    fireEvent.change(searchInput, { target: { value: 'Clock' } });

    expect(screen.getByText('Analog Clock React app')).toBeInTheDocument();
    expect(screen.queryByText('Simple Design System')).not.toBeInTheDocument();
  });

  it('triggers callbacks', () => {
    const onNewChat = vi.fn();
    const onClear = vi.fn();
    const onCollapse = vi.fn();

    render(
      <ChatSidebar
        onNewChat={onNewChat}
        onClearKnowledgeBase={onClear}
        onCollapse={onCollapse}
      />
    );

    fireEvent.click(screen.getByText('New Chat'));
    expect(onNewChat).toHaveBeenCalled();

    fireEvent.click(screen.getByText('Clear knowledge base'));
    expect(onClear).toHaveBeenCalled();

    const collapseBtn = screen.getByAltText('Sidebar');
    fireEvent.click(collapseBtn);
    expect(onCollapse).toHaveBeenCalled();
  });

  it('allows selecting a chat', () => {
    render(<ChatSidebar onNewChat={() => {}} onClearKnowledgeBase={() => {}} onCollapse={() => {}} />);
    
    const chatBtn = screen.getByText('Figma variable planning');
    fireEvent.click(chatBtn);
    
    expect(chatBtn.parentElement).toHaveClass('bg-gray-100');
  });
});
