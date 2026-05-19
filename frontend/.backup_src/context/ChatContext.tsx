/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, type ReactNode } from "react";
import type { ChatResponse } from "../api";

export interface ChatMessage {
  id: number;
  role: "user" | "assistant" | "system";
  content: string;
  metadata?: ChatResponse;
}

interface ChatContextType {
  messages: ChatMessage[];
  setMessages: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  isSending: boolean;
  setIsSending: React.Dispatch<React.SetStateAction<boolean>>;
  status: string;
  setStatus: React.Dispatch<React.SetStateAction<string>>;
  activeView: "home" | "chat" | "upload";
  setActiveView: React.Dispatch<React.SetStateAction<"home" | "chat" | "upload">>;
  isSidebarOpen: boolean;
  setIsSidebarOpen: React.Dispatch<React.SetStateAction<boolean>>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isSending, setIsSending] = useState(false);
  const [status, setStatus] = useState("Backend ready at /api");
  const [activeView, setActiveView] = useState<"home" | "chat" | "upload">("home");
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <ChatContext.Provider
      value={{
        messages,
        setMessages,
        isSending,
        setIsSending,
        status,
        setStatus,
        activeView,
        setActiveView,
        isSidebarOpen,
        setIsSidebarOpen,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChatContext must be used within a ChatProvider");
  }
  return context;
}
