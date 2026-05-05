interface IconSidebarProps {
  onLogoClick?: () => void;
  onHomeClick?: () => void;
  onDocumentClick?: () => void;
  activeView?: 'home' | 'chat' | 'upload';
}

export default function IconSidebar({ onLogoClick, onHomeClick, onDocumentClick, activeView = 'home' }: IconSidebarProps) {
  return (
    <aside className="flex flex-col items-center gap-6 pt-5 w-[72px] min-w-[72px] bg-[#fcfcfc] h-full shadow-[4px_0_16px_rgba(0,0,0,0.2)] z-10">
      {/* App Logo */}
      <button onClick={onLogoClick} className="flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br from-violet-300 via-purple-200 to-indigo-300 hover:opacity-90 transition-opacity duration-150 cursor-pointer border-0">
        <img src="/logo.svg" alt="Logo" className="w-6 h-6" />
      </button>

      {/* Navigation Icons */}
      <div className="flex flex-col gap-4 w-full items-center">
        {/* Home Icon */}
        <button 
          onClick={onHomeClick}
          className={`flex items-center justify-center w-11 h-11 rounded-lg transition-colors duration-150 group cursor-pointer border-0 ${activeView === 'home' || activeView === 'chat' ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-100 bg-transparent'}`}
        >
          <img src="/home.svg" alt="Home" className="w-6 h-6 opacity-80" />
        </button>

        {/* Library / Book Icon */}
        <button 
          onClick={onDocumentClick}
          className={`flex items-center justify-center w-11 h-11 rounded-lg transition-colors duration-150 group cursor-pointer border-0 ${activeView === 'upload' ? 'bg-indigo-100 text-indigo-600' : 'hover:bg-gray-100 bg-transparent'}`}
        >
          <img src="/document.svg" alt="Library" className="w-6 h-6 opacity-80" />
        </button>
      </div>
    </aside>
  );
}