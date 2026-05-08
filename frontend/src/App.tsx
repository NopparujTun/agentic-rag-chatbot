import IconSidebar from "./components/IconSidebar";
import ChatSidebar from "./components/ChatSidebar";
import MainContent from "./components/MainContent";
import UploadPage from "./components/UploadPage";
import HomePage from "./components/HomePage";
import { useChatContext } from "./context/ChatContext";
import { useChat } from "./hooks/useChat";
import { useUpload } from "./hooks/useUpload";

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
