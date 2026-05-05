import ToolButton from './ToolButton';
import ChatInput from './ChatInput';
import MessageItem from './MessageItem';
import type { ChatMessage } from '../App';

const toolsRow1 = [
  { emoji: '📄', label: 'Summarize text' },
  { emoji: '📊', label: 'Analyze data', badge: 'NEW' },
  { emoji: '👁️', label: 'Analyze image' },
  { emoji: '🖼️', label: 'Create image' },
  { emoji: '📰', label: 'Search academic papers' },
];

const toolsRow2 = [
  { emoji: '🎬', label: 'Summarize Youtube video' },
  { emoji: '🌐', label: 'Search online' },
];

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

      {/* Center Block */}
      <div className={`flex flex-col items-center gap-6 flex-1 w-full ${hasMessages ? 'justify-start overflow-hidden' : 'justify-center'}`}>

        {/* AI Avatar / Empty State */}
        <div className={`flex flex-col items-center gap-4 ${hasMessages ? 'hidden' : 'mt-20'}`}>
          <div className="w-16 h-16 rounded-full bg-black flex items-center justify-center shadow-md">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2a2 2 0 0 1 2 2c-.001 5-2.002 6.5-6 7a10 10 0 0 0 4 11" />
              <path d="M12 2a2 2 0 0 0-2 2c.001 5 2.002 6.5 6 7a10 10 0 0 1-4 11" />
            </svg>
          </div>
        </div>

        {/* Greeting */}
        <h2 className={`text-2xl md:text-3xl font-semibold text-[#0d0d0d] text-center tracking-tight ${hasMessages ? 'hidden' : ''}`}>
          How can I help you today?
        </h2>

        {/* Available Tools */}
        <div className={`flex flex-col items-center gap-3 w-full ${hasMessages ? 'hidden' : ''}`}>
          <span className="text-xs text-[#aaa] font-medium uppercase tracking-widest">Available tools</span>

          {/* Row 1 */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            {toolsRow1.map(tool => (
              <ToolButton key={tool.label} emoji={tool.emoji} label={tool.label} badge={tool.badge} />
            ))}
          </div>

          {/* Row 2 */}
          <div className="flex flex-wrap items-center justify-center gap-2">
            {toolsRow2.map(tool => (
              <ToolButton key={tool.label} emoji={tool.emoji} label={tool.label} />
            ))}
          </div>
        </div>

        {hasMessages && (
          <div className="w-full flex-1 overflow-y-auto pr-2 flex flex-col" style={{ scrollBehavior: 'smooth' }}>
            {messages.map((message, index) => {
              const isLatestAssistantMessage = 
                message.role === 'assistant' && 
                index === messages.length - 1;

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
                message={{ id: 0, role: 'assistant', content: '' }}
                isLatestAssistantMessage={true}
                isThinking={true}
              />
            )}
          </div>
        )}
      </div>

      {/* Chat Input pinned to bottom */}
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
