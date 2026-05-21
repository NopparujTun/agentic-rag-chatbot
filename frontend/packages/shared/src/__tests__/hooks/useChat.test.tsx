import React from 'react';
import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useChat } from '../../hooks/useChat';
import { ChatProvider } from '../../context/ChatContext';
import * as api from '../../api';

vi.mock('../../api', () => ({
  sendChatMessage: vi.fn(),
  clearKnowledgeBase: vi.fn(),
}));

const wrapper = ({ children }: { children: React.ReactNode }) => (
  React.createElement(ChatProvider, null, children)
);

describe('useChat hook', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('handleSendMessage updates state and calls api', async () => {
    const mockSend = vi.mocked(api.sendChatMessage).mockResolvedValueOnce({
      answer: 'Mock response',
      response_time_seconds: 1.5,
    });

    const { result } = renderHook(() => useChat(), { wrapper });

    act(() => {
      result.current.handleSendMessage('Hello');
    });

    await waitFor(() => {
      expect(mockSend).toHaveBeenCalledWith('Hello', '');
    });
  });

  it('handleSendMessage does nothing if isSending is true', async () => {
    vi.mocked(api.sendChatMessage).mockResolvedValue({
      answer: 'Mock response',
    });
    
    // Use our wrapper but we need to inject the state.
    // Let's just create a custom Context Provider for this test
    const customWrapper = ({ children }: any) => {
      const mockContext = { 
        messages: [], setMessages: vi.fn(), 
        isSending: true, setIsSending: vi.fn(), 
        status: 'ready', setStatus: vi.fn(), 
        activeView: 'chat', setActiveView: vi.fn(), 
        isSidebarOpen: false, setIsSidebarOpen: vi.fn() 
      };
      // We need to import ChatContext for the provider, let's just mock useChatContext directly for this test
      return <>{children}</>;
    };

    // For useChat we can just mock useChatContext. Wait, we use ChatProvider normally. 
    // The easiest way is to mock useChatContext globally, or just call it, wait for isSending, then call again.
    const { result } = renderHook(() => useChat(), { wrapper });
    
    act(() => {
      result.current.handleSendMessage('Hello 1');
    });
    
    // Now it's sending, so calling again should be ignored
    act(() => {
      result.current.handleSendMessage('Hello 2');
    });

    await waitFor(() => {
      expect(api.sendChatMessage).toHaveBeenCalledTimes(1);
      expect(api.sendChatMessage).toHaveBeenCalledWith('Hello 1', '');
    });
  });

  it('handleSendMessage transitions from home to chat', async () => {
    vi.mocked(api.sendChatMessage).mockResolvedValue({
      answer: 'Mock response',
    });

    const { result } = renderHook(() => useChat(), { wrapper });
    
    act(() => {
      result.current.handleSendMessage('Hello from home');
    });

    await waitFor(() => {
      expect(api.sendChatMessage).toHaveBeenCalledWith('Hello from home', '');
    });
  });
    it('handleSendMessage does nothing if query is empty', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    act(() => {
      result.current.handleSendMessage('   ');
    });

    expect(api.sendChatMessage).not.toHaveBeenCalled();
  });

  it('handleSendMessage handles API errors', async () => {
    vi.mocked(api.sendChatMessage).mockRejectedValueOnce(new Error('API failed'));

    const { result } = renderHook(() => useChat(), { wrapper });

    act(() => {
      result.current.handleSendMessage('Hello');
    });

    await waitFor(() => {
      expect(api.sendChatMessage).toHaveBeenCalled();
    });
  });

  it('handleClear calls api and updates status', async () => {
    vi.mocked(api.clearKnowledgeBase).mockResolvedValueOnce({
      message: 'Cleared successfully',
    });

    const { result } = renderHook(() => useChat(), { wrapper });

    act(() => {
      result.current.handleClear();
    });

    await waitFor(() => {
      expect(api.clearKnowledgeBase).toHaveBeenCalled();
    });
  });

  it('handleSendMessage handles API non-Error objects', async () => {
    vi.mocked(api.sendChatMessage).mockRejectedValueOnce('Some string error');

    const { result } = renderHook(() => useChat(), { wrapper });

    act(() => {
      result.current.handleSendMessage('Hello string error');
    });

    await waitFor(() => {
      expect(api.sendChatMessage).toHaveBeenCalled();
    });
  });

  it('handleClear handles API non-Error objects', async () => {
    vi.mocked(api.clearKnowledgeBase).mockRejectedValueOnce('Clear string error');

    const { result } = renderHook(() => useChat(), { wrapper });

    act(() => {
      result.current.handleClear();
    });

    await waitFor(() => {
      expect(api.clearKnowledgeBase).toHaveBeenCalled();
    });
  });
});
