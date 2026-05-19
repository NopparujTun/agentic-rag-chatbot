import { useRef, useEffect } from "react";
import { type ChatMessage, useTypingEffect, ThinkingIndicator } from "@mfa/shared";
import MessageMetadata from "./MessageMetadata";

interface MessageItemProps {
  message: ChatMessage;
  isLatestAssistantMessage: boolean;
  isThinking?: boolean;
  thinkingStep?: number;
}

export default function MessageItem({
  message,
  isLatestAssistantMessage,
  isThinking = false,
  thinkingStep,
}: MessageItemProps) {
  const shouldStream = isLatestAssistantMessage && message.role === "assistant" && !isThinking;
  const { displayedText, isTyping } = useTypingEffect(message.content, shouldStream);

  const messageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isTyping && messageRef.current) {
      messageRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [displayedText, isTyping]);

  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="mx-auto w-full max-w-3xl my-4 text-center">
        <div className="inline-block px-4 py-2 rounded-lg bg-red-50 text-red-800 border border-red-200 text-sm">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="w-full flex justify-center py-6" ref={messageRef}>
      <div className={`flex w-full max-w-3xl gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2a2 2 0 0 1 2 2c-.001 5-2.002 6.5-6 7a10 10 0 0 0 4 11" />
              <path d="M12 2a2 2 0 0 0-2 2c.001 5 2.002 6.5 6 7a10 10 0 0 1-4 11" />
            </svg>
          </div>
        )}

        <div className={`flex flex-col gap-2 max-w-[85%] ${isUser ? "items-end" : "items-start"}`}>
          {isThinking && !isUser && (
            <div className="py-1">
              <ThinkingIndicator step={thinkingStep} />
            </div>
          )}
          {!isThinking && (
            <div
              className={`text-base leading-relaxed ${
                isUser
                  ? "bg-[#f4f4f4] text-[#0d0d0d] px-5 py-3 rounded-3xl rounded-tr-sm"
                  : "text-[#0d0d0d] py-1"
              }`}
            >
              <p className="whitespace-pre-wrap">{displayedText}</p>
              {isTyping && (
                <span className="inline-block w-2 h-4 ml-1 bg-black animate-pulse align-middle" />
              )}
            </div>
          )}

          {!isTyping && !isThinking && message.metadata && (
            <MessageMetadata metadata={message.metadata} />
          )}
        </div>
      </div>
    </div>
  );
}
