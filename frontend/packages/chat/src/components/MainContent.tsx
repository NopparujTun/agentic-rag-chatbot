import { ChatInput, HeroSection, type ChatMessage } from "@mfa/shared";
import MessageItem from "./MessageItem";

interface MainContentProps {
  messages: ChatMessage[];
  isSending: boolean;
  status: string;
  onSendMessage: (message: string) => void;
  onUploadDocuments: (files: FileList) => void;
}

export default function MainContent({
  messages,
  isSending,
  status,
  onSendMessage,
  onUploadDocuments,
}: MainContentProps) {
  const hasMessages = messages.length > 0;

  return (
    <main className="flex-1 bg-white h-full flex flex-col items-center justify-between py-6 px-4 md:px-8 overflow-hidden font-sans">
      <div
        className={`flex flex-col items-center gap-6 flex-1 w-full ${hasMessages ? "justify-start overflow-hidden" : "justify-center"}`}
      >
        {!hasMessages && <HeroSection showDescription={false} />}

        {hasMessages && (
          <div
            className="w-full flex-1 overflow-y-auto pr-2 flex flex-col"
            style={{ scrollBehavior: "smooth" }}
          >
            {messages.map((message, index) => {
              const isLatestAssistantMessage =
                message.role === "assistant" && index === messages.length - 1;

              return (
                <MessageItem
                  key={message.id}
                  message={message}
                  isLatestAssistantMessage={isLatestAssistantMessage}
                />
              );
            })}

            {isSending && (
              <MessageItem
                message={{ id: 0, role: "assistant", content: "" }}
                isLatestAssistantMessage={true}
                isThinking={true}
              />
            )}
          </div>
        )}
      </div>

      <div className="w-full max-w-2xl">
        <p className="mb-2 text-center text-xs text-[#777]">{status}</p>
        <ChatInput
          isSending={isSending}
          onSendMessage={onSendMessage}
          onUploadDocuments={onUploadDocuments}
        />
      </div>
    </main>
  );
}
