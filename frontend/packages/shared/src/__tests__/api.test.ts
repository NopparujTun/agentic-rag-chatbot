import { describe, it, expect, vi, beforeEach } from 'vitest';
import { sendChatMessage, uploadDocuments, clearKnowledgeBase } from '../../src/api';

const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('API functions', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('sendChatMessage sends query and history', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ answer: 'Test answer' }),
    });

    const result = await sendChatMessage('hello', 'history');
    
    expect(mockFetch).toHaveBeenCalledWith('/api/chat', expect.objectContaining({
      method: 'POST',
      body: JSON.stringify({ query: 'hello', chat_history: 'history' }),
    }));
    expect(result).toEqual({ answer: 'Test answer' });
  });

  it('sendChatMessage handles failure', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: 'Bad Request' }),
    });

    await expect(sendChatMessage('hello', '')).rejects.toThrow('Bad Request');
  });

  it('sendChatMessage handles failure without detail', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({}),
    });

    await expect(sendChatMessage('hello', '')).rejects.toThrow('Request failed with status 500');
  });

  it('uploadDocuments sends FormData', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Uploaded', files_processed: ['test.pdf'] }),
    });

    const file = new File([''], 'test.pdf');
    const dt = [file] as unknown as FileList;
    
    const result = await uploadDocuments(dt);
    
    expect(mockFetch).toHaveBeenCalledWith('/api/upload', expect.objectContaining({
      method: 'POST',
    }));
    expect(result).toEqual({ message: 'Uploaded', files_processed: ['test.pdf'] });
  });

  it('clearKnowledgeBase sends POST to /api/clear', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ message: 'Cleared' }),
    });

    const result = await clearKnowledgeBase();
    
    expect(mockFetch).toHaveBeenCalledWith('/api/clear', expect.objectContaining({
      method: 'POST',
    }));
    expect(result).toEqual({ message: 'Cleared' });
  });
});
