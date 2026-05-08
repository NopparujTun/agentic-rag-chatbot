import { useMemo } from "react";
import { useChatContext } from "../context/ChatContext";
import { sendChatMessage, clearKnowledgeBase } from "../api";

export function useChat() {
  const {
    messages,
    setMessages,
    isSending,
    setIsSending,
    setStatus,
    activeView,
    setActiveView,
    setIsSidebarOpen,
  } = useChatContext();

  const chatHistory = useMemo(
    () =>
      messages
        .filter((message) => message.role !== "system")
        .map((message) => `${message.role}: ${message.content}`)
        .join("\n"),
    [messages]
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
      setMessages([]);
    }

    const userMessage = {
      id: Date.now(),
      role: "user" as const,
      content: trimmed,
    };

    setMessages((current) => isStartingFromHome ? [userMessage] : [...current, userMessage]);
    setIsSending(true);
    setStatus("Thinking...");

    try {
      const currentHistory = isStartingFromHome ? "" : chatHistory;
      const response = await sendChatMessage(trimmed, currentHistory);
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "assistant" as const,
          content: response.answer,
          metadata: response,
        },
      ]);
      setStatus(
        response.response_time_seconds
          ? `Answered in ${response.response_time_seconds}s`
          : "Answer received"
      );
    } catch (error) {
      const message = error instanceof Error ? error.message : "Chat request failed";
      setMessages((current) => [
        ...current,
        {
          id: Date.now() + 1,
          role: "system" as const,
          content: message,
        },
      ]);
      setStatus(message);
    } finally {
      setIsSending(false);
    }
  }

  async function handleClear() {
    setStatus("Clearing knowledge base...");
    try {
      const response = await clearKnowledgeBase();
      setMessages([
        {
          id: Date.now(),
          role: "system" as const,
          content: response.message,
        },
      ]);
      setStatus(response.message);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Clear failed";
      setStatus(message);
    }
  }

  return {
    handleSendMessage,
    handleClear,
  };
}
