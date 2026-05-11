interface ToolButtonProps {
  emoji: string;
  label: string;
  badge?: string;
}

export default function ToolButton({ emoji, label, badge }: ToolButtonProps) {
  return (
    <button
      className="
      flex items-center gap-2 px-4 py-2 rounded-full
      bg-white border border-[#e5e5e5]
      text-[#1a1a1a] text-sm font-medium
      hover:bg-[#f5f5f5] hover:border-[#d0d0d0] hover:shadow-sm
      active:scale-95
      transition-all duration-150 cursor-pointer
      whitespace-nowrap
    "
    >
      <span className="text-base leading-none">{emoji}</span>
      <span>{label}</span>
      {badge && (
        <span className="ml-0.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700 border border-amber-200 uppercase tracking-wide">
          {badge}
        </span>
      )}
    </button>
  );
}
