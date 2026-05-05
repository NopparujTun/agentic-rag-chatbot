import { useState } from 'react';

const chats = [
  { id: 1, title: 'Analog Clock React app' },
  { id: 2, title: 'Figma variable planning' },
  { id: 3, title: 'Simple Design System' },
  { id: 4, title: 'OKCLH token algorithm' },
  { id: 5, title: 'Component naming advice' },
];

interface ChatSidebarProps {
  onNewChat: () => void;
  onClearKnowledgeBase: () => void;
  onCollapse: () => void;
}

export default function ChatSidebar({ onNewChat, onClearKnowledgeBase, onCollapse }: ChatSidebarProps) {
  const [activeChat, setActiveChat] = useState(1);
  const [search, setSearch] = useState('');

  const filtered = chats.filter(c =>
    c.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <aside className="flex flex-col w-[280px] min-w-[280px] bg-white h-full p-4 border-r border-gray-100">

      {/* Top Row */}
      <div className="flex items-center justify-between mb-6">
        <button
          onClick={onNewChat}
          className="flex items-center gap-2 text-gray-900 font-semibold text-base hover:opacity-70 transition-opacity cursor-pointer border-0 bg-transparent p-0"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="16" />
            <line x1="8" y1="12" x2="16" y2="12" />
          </svg>
          New Chat
        </button>
        <button onClick={onCollapse} className="text-gray-900 hover:opacity-70 transition-opacity cursor-pointer border-0 bg-transparent p-1 rounded-md">
          <img src="/sidebar.svg" alt="Sidebar" className="w-5 h-5" />
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative mb-6">
        <input
          type="text"
          placeholder="Search"
          value={search}
          onChange={e => setSearch(e.target.value)}
          className="w-full bg-white text-gray-900 placeholder-gray-400 text-sm rounded-full pl-4 pr-10 py-2 outline-none focus:ring-1 focus:ring-gray-300 border border-gray-200 transition-all"
        />
        <svg
          className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-900 pointer-events-none"
          width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
        >
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      </div>

      {/* Section Label */}
      <span className="text-sm font-semibold text-gray-500 mb-2 block px-2">
        Chats
      </span>

      {/* Chat List */}
      <nav className="flex flex-col gap-1 flex-1 overflow-y-auto">
        {filtered.map(chat => (
          <button
            key={chat.id}
            onClick={() => setActiveChat(chat.id)}
            className={`
              w-full text-left px-3 py-2 rounded-lg text-sm transition-colors duration-100 cursor-pointer border-0
              ${activeChat === chat.id
                ? 'bg-gray-100 text-gray-900 font-medium'
                : 'bg-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }
            `}
          >
            <span className="line-clamp-1">{chat.title}</span>
          </button>
        ))}
      </nav>
      <button
        onClick={onClearKnowledgeBase}
        className="mt-4 w-full rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-left text-sm font-medium text-red-700 hover:bg-red-100 transition-colors"
      >
        Clear knowledge base
      </button>
    </aside>
  );
}
