import { useMemo, useState } from "react";
import IconSidebar from "./components/IconSidebar";
import ChatSidebar from "./components/ChatSidebar";
import MainContent from "./components/MainContent";
import UploadPage from "./components/UploadPage";
import HomePage from "./components/HomePage";
import {
  clearKnowledgeBase,
  sendChatMessage,
  uploadDocuments,
  type ChatResponse,
} from "./api";

export interface ChatMessage {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  metadata?: ChatResponse;
}

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [status, setStatus] = useState("Backend ready at /api");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [activeView, setActiveView] = useState<"home" | "chat" | "upload">("home");

  const chatHistory = useMemo(
    () =>
      messages
        .filter((message) => message.role !== "system")
        .map((message) => `${message.role}: ${message.content}`)
        .join("\n"),
    [messages],
  );

  async function handleSendMessage(query: string) {
    const trimmed = query.trim();

    if (!trimmed || isSending) {
      return;
    }

    const isStartingFromHome = activeView === "home";

    if (isStartingFromHome) {
      setActiveView("chat");
      setIsSidebarOpen(true);
      setMessages([]); // Start a fresh chat if typing from home
    }

    const userMessage: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: trimmed,
    };

    setMessages((current) => isStartingFromHome ? [userMessage] : [...current, userMessage]);
    setIsSending(true);
    setStatus("Thinking...");

    try {
      // Use empty history if starting from home, otherwise use current history
      const currentHistory = isStartingFromHome ? "" : chatHistory;
      const response = await sendChatMessage(trimmed, currentHistory);
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: response.answer,
          metadata: response,
        },
      ]);
      setStatus(
        response.response_time_seconds
          ? `Answered in ${response.response_time_seconds}s`
          : "Answer received",
      );
    } catch (error) {
      const message =
        error instanceof Error ? error.message : "Chat request failed";
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "system",
          content: message,
        },
      ]);
      setStatus(message);
    } finally {
      setIsSending(false);
    }
  }

  async function handleUpload(files: FileList) {
    if (!files.length) {
      return;
    }

    setStatus("Uploading documents...");

    try {
      const response = await uploadDocuments(files);
      const fileList = response.files_processed.join(", ");
      setStatus(`Uploaded ${response.files_processed.length} file(s)`);
      setMessages((current) => [
        ...current,
        {
          id: Date.now(),
          role: "system",
          content: `${response.message}: ${fileList}. Indexed ${response.total_chunks} chunks.`,
        },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Upload failed";
      setStatus(message);
      setMessages((current) => [
        ...current,
        {
          id: Date.now(),
          role: "system",
          content: message,
        },
      ]);
    }
  }

  async function handleClear() {
    setStatus("Clearing knowledge base...");

    try {
      const response = await clearKnowledgeBase();
      setMessages([
        {
          id: Date.now(),
          role: "system",
          content: response.message,
        },
      ]);
      setStatus(response.message);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Clear failed";
      setStatus(message);
    }
  }

  return (
    <div className="flex h-screen w-screen overflow-hidden min-w-[1024px]">
      <IconSidebar
        onLogoClick={() => setIsSidebarOpen(!isSidebarOpen)}
        onHomeClick={() => {
          setActiveView("home");
          setIsSidebarOpen(false);
        }}
        onDocumentClick={() => {
          setActiveView("upload");
          setIsSidebarOpen(false);
        }}
        activeView={activeView}
      />
      {isSidebarOpen && activeView !== "upload" && (
        <ChatSidebar
          onNewChat={() => {
            setMessages([]);
            setActiveView("chat");
            setIsSidebarOpen(true);
          }}
          onClearKnowledgeBase={handleClear}
          onCollapse={() => setIsSidebarOpen(false)}
        />
      )}
      {activeView === "upload" ? (
        <UploadPage onUpload={handleUpload} status={status} />
      ) : activeView === "home" ? (
        <HomePage
          isSending={isSending}
          status={status}
          onSendMessage={handleSendMessage}
          onUploadDocuments={handleUpload}
        />
      ) : (
        <MainContent
          messages={messages}
          isSending={isSending}
          status={status}
          onSendMessage={handleSendMessage}
          onUploadDocuments={handleUpload}
        />
      )}
    </div>
  );
}
