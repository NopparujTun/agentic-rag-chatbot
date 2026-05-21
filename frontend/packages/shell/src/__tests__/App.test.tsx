import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import App from '../../src/App';
import * as shared from '@mfa/shared';

vi.mock('chat/MainContent', () => ({
  default: () => <div data-testid="main-content" />
}));

vi.mock('chat/ChatSidebar', () => ({
  default: ({ onCollapse, onHomeClick, onNewChat, onClearKnowledgeBase }: any) => (
    <div data-testid="chat-sidebar">
      <button data-testid="sidebar-collapse" onClick={onCollapse}>Collapse</button>
      <button data-testid="sidebar-new" onClick={onNewChat}>New</button>
      <button data-testid="sidebar-clear" onClick={onClearKnowledgeBase}>Clear</button>
    </div>
  )
}));

vi.mock('upload/UploadPage', () => ({
  default: () => <div data-testid="upload-page" />
}));

vi.mock('../../src/components/HomePage', () => ({
  default: () => <div data-testid="home-page" />
}));

vi.mock('../../src/components/IconSidebar', () => ({
  default: ({ onHomeClick, onDocumentClick, onLogoClick }: any) => (
    <div data-testid="icon-sidebar">
      <button data-testid="icon-logo" onClick={onLogoClick}>Logo</button>
      <button data-testid="icon-home" onClick={onHomeClick}>Home</button>
      <button data-testid="icon-doc" onClick={onDocumentClick}>Doc</button>
    </div>
  )
}));

vi.mock('@mfa/shared', async (importOriginal) => {
  return {
    useChatContext: vi.fn(),
    useChat: () => ({ handleSendMessage: vi.fn(), handleClear: vi.fn() }),
    useUpload: () => ({ handleUpload: vi.fn() }),
  };
});

describe('App Component', () => {
  it('renders home view correctly', async () => {
    vi.mocked(shared.useChatContext).mockReturnValue({
      messages: [], setMessages: vi.fn(),
      isSending: false, status: 'ready',
      activeView: 'home', setActiveView: vi.fn(),
      isSidebarOpen: false, setIsSidebarOpen: vi.fn(),
    } as any);

    render(
      <React.Suspense fallback={<div>Loading...</div>}>
        <App />
      </React.Suspense>
    );
    expect(await screen.findByTestId('home-page')).toBeInTheDocument();
  });

  it('renders upload view correctly', async () => {
    vi.mocked(shared.useChatContext).mockReturnValue({
      messages: [], setMessages: vi.fn(),
      isSending: false, status: 'ready',
      activeView: 'upload', setActiveView: vi.fn(),
      isSidebarOpen: false, setIsSidebarOpen: vi.fn(),
    } as any);

    render(
      <React.Suspense fallback={<div>Loading...</div>}>
        <App />
      </React.Suspense>
    );
    expect(await screen.findByTestId('upload-page')).toBeInTheDocument();
  });

  it('renders chat view with sidebar correctly', async () => {
    vi.mocked(shared.useChatContext).mockReturnValue({
      messages: [], setMessages: vi.fn(),
      isSending: false, status: 'ready',
      activeView: 'chat', setActiveView: vi.fn(),
      isSidebarOpen: true, setIsSidebarOpen: vi.fn(),
    } as any);

    render(
      <React.Suspense fallback={<div>Loading...</div>}>
        <App />
      </React.Suspense>
    );
    expect(await screen.findByTestId('main-content')).toBeInTheDocument();
    expect(await screen.findByTestId('chat-sidebar')).toBeInTheDocument();
  });

  it('handles sidebar actions', async () => {
    const setIsSidebarOpen = vi.fn();
    const setActiveView = vi.fn();
    vi.mocked(shared.useChatContext).mockReturnValue({
      messages: [], setMessages: vi.fn(),
      isSending: false, status: 'ready',
      activeView: 'chat', setActiveView,
      isSidebarOpen: true, setIsSidebarOpen,
    } as any);

    render(
      <React.Suspense fallback={<div>Loading...</div>}>
        <App />
      </React.Suspense>
    );
    
    await screen.findByTestId('chat-sidebar');
    
    fireEvent.click(screen.getByTestId('sidebar-collapse'));
    expect(setIsSidebarOpen).toHaveBeenCalledWith(false);

    fireEvent.click(screen.getByTestId('icon-home'));
    expect(setActiveView).toHaveBeenCalledWith('home');
    
    fireEvent.click(screen.getByTestId('icon-doc'));
    expect(setActiveView).toHaveBeenCalledWith('upload');
  });
});
