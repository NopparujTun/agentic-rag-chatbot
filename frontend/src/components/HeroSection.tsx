import ToolButton from './ToolButton';

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

interface HeroSectionProps {
  showDescription?: boolean;
}

export default function HeroSection({ showDescription = false }: HeroSectionProps) {
  return (
    <>
      <div className="flex flex-col items-center gap-4 mt-6">
        <div className="w-16 h-16 rounded-full bg-black flex items-center justify-center shadow-md">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 2a2 2 0 0 1 2 2c-.001 5-2.002 6.5-6 7a10 10 0 0 0 4 11" />
            <path d="M12 2a2 2 0 0 0-2 2c.001 5 2.002 6.5 6 7a10 10 0 0 1-4 11" />
          </svg>
        </div>
      </div>

      <h2 className="text-2xl md:text-3xl font-semibold text-[#0d0d0d] text-center tracking-tight">
        How can I help you today?
      </h2>

      {showDescription && (
        <p className="text-center text-gray-500 max-w-2xl text-sm md:text-base px-4">
          This is an intelligent AI chatbot powered by Retrieval-Augmented Generation (RAG). It can help you analyze uploaded documents, answer complex questions using internal knowledge, and streamline your daily workflow. Feel free to explore the available tools or start a conversation!
        </p>
      )}

      <div className="flex flex-col items-center gap-3 w-full mt-4">
        <span className="text-xs text-[#aaa] font-medium uppercase tracking-widest">Available tools</span>

        <div className="flex flex-wrap items-center justify-center gap-2">
          {toolsRow1.map(tool => (
            <ToolButton key={tool.label} emoji={tool.emoji} label={tool.label} badge={tool.badge} />
          ))}
        </div>

        <div className="flex flex-wrap items-center justify-center gap-2">
          {toolsRow2.map(tool => (
            <ToolButton key={tool.label} emoji={tool.emoji} label={tool.label} />
          ))}
        </div>
      </div>
    </>
  );
}
