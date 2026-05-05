import { useRef, useEffect } from 'react';
import type { ChatMessage } from '../App';
import { useTypingEffect } from '../hooks/useTypingEffect';
import { ThinkingIndicator } from './ThinkingIndicator';

interface MessageItemProps {
  message: ChatMessage;
  isLatestAssistantMessage: boolean;
  isThinking?: boolean;
  thinkingStep?: number;
}

export default function MessageItem({ message, isLatestAssistantMessage, isThinking = false, thinkingStep }: MessageItemProps) {
  // Only apply typing effect to the latest assistant message
  const shouldStream = isLatestAssistantMessage && message.role === 'assistant' && !isThinking;
  const { displayedText, isTyping } = useTypingEffect(message.content, shouldStream);
  
  // Ref for auto-scrolling during typing
  const messageRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isTyping && messageRef.current) {
      messageRef.current.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, [displayedText, isTyping]);

  const isUser = message.role === 'user';
  const isSystem = message.role === 'system';

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
      <div className={`flex w-full max-w-3xl gap-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
        
        {/* Assistant Avatar */}
        {!isUser && (
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a2 2 0 0 1 2 2c-.001 5-2.002 6.5-6 7a10 10 0 0 0 4 11" />
              <path d="M12 2a2 2 0 0 0-2 2c.001 5 2.002 6.5 6 7a10 10 0 0 1-4 11" />
            </svg>
          </div>
        )}

        <div className={`flex flex-col gap-2 max-w-[85%] ${isUser ? 'items-end' : 'items-start'}`}>
          {isThinking && !isUser ? (
            <div className="py-1">
              <ThinkingIndicator step={thinkingStep} />
            </div>
          ) : (
            <div
              className={`text-base leading-relaxed ${
                isUser
                  ? 'bg-[#f4f4f4] text-[#0d0d0d] px-5 py-3 rounded-3xl rounded-tr-sm'
                  : 'text-[#0d0d0d] py-1'
              }`}
            >
              <p className="whitespace-pre-wrap">{displayedText}</p>
              {isTyping && <span className="inline-block w-2 h-4 ml-1 bg-black animate-pulse align-middle" />}
            </div>
          )}

          {/* Metadata Section - Only show after typing is done */}
          {!isTyping && !isThinking && message.metadata && (
            <div className="flex flex-col gap-2 w-full mt-2">

              {message.metadata.steps && message.metadata.steps.length > 0 && (
                <details className="mt-1 text-xs text-gray-600 border border-gray-200 rounded-xl overflow-hidden w-full bg-white shadow-sm hover:shadow transition-shadow">
                  <summary className="cursor-pointer font-medium px-4 py-2 bg-gray-50 hover:bg-gray-100 transition-colors">
                    🧠 Thought Process ({message.metadata.steps.length} steps)
                  </summary>
                  <div className="p-3 bg-white flex flex-col gap-3 max-h-60 overflow-y-auto border-t border-gray-100">
                    {message.metadata.steps.map((step, idx) => (
                      <div key={idx} className="flex flex-col gap-1 border-b border-gray-50 pb-2 last:border-0 last:pb-0">
                        <div className="font-semibold text-gray-700">🛠️ Tool: {step.tool}</div>
                        <div className="text-gray-500 bg-gray-50 p-1.5 rounded-md font-mono text-[10px]">Input: {JSON.stringify(step.tool_input)}</div>
                        <div className="text-gray-600 bg-blue-50/50 p-1.5 rounded-md truncate" title={step.observation}>
                          Result: {step.observation.length > 100 ? step.observation.substring(0, 100) + '...' : step.observation}
                        </div>
                      </div>
                    ))}
                  </div>
                </details>
              )}

              {message.metadata.sources && message.metadata.sources.length > 0 && (
                <details className="mt-1 text-xs text-gray-600 border border-gray-200 rounded-xl overflow-hidden w-full bg-white shadow-sm hover:shadow transition-shadow">
                  <summary className="cursor-pointer font-medium px-4 py-2 bg-gray-50 hover:bg-gray-100 transition-colors">
                    📚 Sources ({message.metadata.sources.length})
                  </summary>
                  <div className="p-3 bg-white flex flex-col gap-3 max-h-60 overflow-y-auto border-t border-gray-100">
                    {message.metadata.sources.map((source, idx) => (
                      <div key={idx} className="flex flex-col gap-1 border border-gray-100 rounded-lg p-2.5 bg-gray-50">
                        <div className="font-semibold text-gray-800 truncate" title={source.metadata?.source || 'Unknown file'}>
                          📄 {source.metadata?.source?.split('/').pop() || source.metadata?.source?.split('\\').pop() || 'Unknown file'}
                        </div>
                        <div className="text-gray-500 line-clamp-3 leading-relaxed mt-1">{source.content}</div>
                      </div>
                    ))}
                  </div>
                </details>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
