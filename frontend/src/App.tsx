import React, { Suspense } from "react";
import IconSidebar from "./components/IconSidebar";
import HomePage from "./components/HomePage";
import { useChatContext, useChat, useUpload } from "@/index";

// Lazy load remote modules
const ChatSidebar = React.lazy(() => import("@/components/ChatSidebar"));
const MainContent = React.lazy(() => import("@/components/MainContent"));
const UploadPage = React.lazy(() => import("@/components/UploadPage"));

export default function App() {
  const {
    messages,
    setMessages,
    isSending,
    status,
    activeView,
    setActiveView,
    isSidebarOpen,
    setIsSidebarOpen,
  } = useChatContext();

  const { handleSendMessage, handleClear } = useChat();
  const { handleUpload } = useUpload();

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
      <Suspense
        fallback={
          <div className="flex flex-1 items-center justify-center text-zinc-500">
            Loading Module...
          </div>
        }
      >
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
      </Suspense>
    </div>
  );
}
