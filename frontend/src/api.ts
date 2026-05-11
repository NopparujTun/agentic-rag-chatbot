/**
 * Represents a source document retrieved from the knowledge base.
 */
export interface Source {
  content: string;
  metadata: Record<string, unknown>;
}

/**
 * Represents a step taken by the Agent during its reasoning process.
 */
export interface AgentStep {
  tool: string;
  tool_input: unknown;
  observation: string;
}

/**
 * The standard response object returned by the chat API.
 */
export interface ChatResponse {
  answer: string;
  sources?: Source[];
  steps?: AgentStep[];
  evaluation?: string;
  response_time_seconds?: number;
}

/**
 * The response object returned when initiating a document upload.
 */
export interface UploadResponse {
  message: string;
  files_processed: string[];
}

/**
 * Helper function to retrieve headers.
 */
const getHeaders = (baseHeaders: Record<string, string> = {}) => {
  return {
    ...baseHeaders,
  };
};

/**
 * Parses the fetch response and throws meaningful errors on failure.
 */
async function parseResponse<T>(response: Response): Promise<T> {
  const payload = await response.json().catch(() => null);

  if (!response.ok) {
    const message =
      payload && typeof payload.detail === "string"
        ? payload.detail
        : `Request failed with status ${response.status}`;
    throw new Error(message);
  }

  return payload as T;
}

/**
 * Sends a chat query to the backend agent.
 * @param query The user's input question.
 * @param chatHistory Formatted string of previous conversation history.
 */
export async function sendChatMessage(query: string, chatHistory: string) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: getHeaders({
      "Content-Type": "application/json",
    }),
    body: JSON.stringify({ query, chat_history: chatHistory }),
  });

  return parseResponse<ChatResponse>(response);
}

/**
 * Uploads a list of documents to the backend for ingestion.
 * @param files The FileList containing the documents.
 */
export async function uploadDocuments(files: FileList) {
  const formData = new FormData();

  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  const response = await fetch("/api/upload", {
    method: "POST",
    headers: getHeaders(),
    body: formData,
  });

  return parseResponse<UploadResponse>(response);
}

/**
 * Clears the user's vector store and knowledge base.
 */
export async function clearKnowledgeBase() {
  const response = await fetch("/api/clear", {
    method: "POST",
    headers: getHeaders(),
  });

  return parseResponse<{ message: string }>(response);
}
