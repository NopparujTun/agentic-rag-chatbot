export interface Source {
  content: string;
  metadata: Record<string, any>;
}

export interface AgentStep {
  tool: string;
  tool_input: any;
  observation: string;
}

export interface ChatResponse {
  answer: string;
  sources?: Source[];
  steps?: AgentStep[];
  evaluation?: string;
  response_time_seconds?: number;
}

export interface UploadResponse {
  message: string;
  total_chunks: number;
  ingestion_time_seconds: number;
  files_processed: string[];
}

async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      payload && typeof payload.detail === 'string'
        ? payload.detail
        : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload as T;
}

export async function sendChatMessage(query: string, chatHistory: string) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, chat_history: chatHistory }),
  });

  return parseResponse<ChatResponse>(response);
}

export async function uploadDocuments(files: FileList) {
  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append('files', file);
  });

  const response = await fetch('/api/upload', {
    method: 'POST',
    body: formData,
  });

  return parseResponse<UploadResponse>(response);
}

export async function clearKnowledgeBase() {
  const response = await fetch('/api/clear', {
    method: 'POST',
  });

  return parseResponse<{ message: string }>(response);
}
