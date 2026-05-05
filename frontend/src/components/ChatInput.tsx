import { type ChangeEvent, type FormEvent, useRef, useState } from 'react';

interface ChatInputProps {
  isSending: boolean;
  onSendMessage: (message: string) => void;
  onUploadDocuments: (files: FileList) => void;
}

export default function ChatInput({
  isSending,
  onSendMessage,
  onUploadDocuments,
}: ChatInputProps) {
  const [value, setValue] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!value.trim() || isSending) {
      return;
    }

    onSendMessage(value);
    setValue('');
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    if (event.target.files) {
      onUploadDocuments(event.target.files);
    }

    event.target.value = '';
  }

  return (
    <form className="w-full max-w-2xl mx-auto" onSubmit={handleSubmit}>
      {/* Main Container */}
      <div className="relative flex flex-col bg-white border border-[#e5e5e5] rounded-[24px] shadow-sm px-4 py-3">
        
        {/* Top: Input and AI Icon */}
        <div className="flex items-center w-full">
          <input
            type="text"
            value={value}
            onChange={e => setValue(e.target.value)}
            disabled={isSending}
            placeholder="Ask anything to start a new chat..."
            className="flex-1 text-[#1a1a1a] text-sm placeholder-[#b0b0b0] outline-none bg-transparent py-1 pr-2"
          />
          {/* Teal Icon */}
          <button className="flex items-center justify-center w-6 h-6 rounded-full text-teal-600 bg-teal-50 hover:bg-teal-100 transition-colors cursor-pointer border-0 flex-shrink-0">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 12a9 9 0 1 1-9-9c2.5 0 4.8 1 6.5 2.5l-2.7 2.7A5.2 5.2 0 1 0 17.2 13H12v-3h9.8c.1.7.2 1.4.2 2z" />
            </svg>
          </button>
        </div>

        {/* Bottom: Toolbar */}
        <div className="flex items-center justify-between mt-3">
          {/* Left tools */}
          <div className="flex items-center gap-2">
            <input
              ref={fileInputRef}
              className="hidden"
              type="file"
              accept="application/pdf,.pdf"
              multiple
              onChange={handleFileChange}
            />
            {/* Attach (+) */}
            <button
              type="button"
              aria-label="Upload PDF documents"
              onClick={() => fileInputRef.current?.click()}
              className="flex items-center justify-center w-8 h-8 rounded-full border border-[#e5e5e5] text-[#555] hover:bg-[#f9f9f9] transition-all cursor-pointer bg-white"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19" />
                <line x1="5" y1="12" x2="19" y2="12" />
              </svg>
            </button>

            {/* Search */}
            <button type="button" className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[#e5e5e5] text-[#555] text-xs font-medium hover:bg-[#f9f9f9] transition-all cursor-pointer bg-white">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <line x1="2" y1="12" x2="22" y2="12" />
                <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              Search
            </button>

            {/* More (...) */}
            <button type="button" className="flex items-center justify-center w-8 h-8 rounded-full border border-[#e5e5e5] text-[#555] hover:bg-[#f9f9f9] transition-all cursor-pointer bg-white leading-none">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <circle cx="12" cy="12" r="1.5" />
                <circle cx="19" cy="12" r="1.5" />
                <circle cx="5" cy="12" r="1.5" />
              </svg>
            </button>
          </div>

          {/* Right tools */}
          <div className="flex items-center gap-2">
            {/* Microphone */}
            <button type="button" className="flex items-center justify-center w-8 h-8 rounded-full text-[#555] hover:bg-[#f9f9f9] transition-all cursor-pointer border-0 bg-transparent">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 2a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V5a3 3 0 0 1 3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="22" />
              </svg>
            </button>

            {/* Send (Up Arrow) */}
            <button
              type="submit"
              disabled={isSending || !value.trim()}
              className="flex items-center justify-center w-8 h-8 rounded-full bg-[#888] hover:bg-[#666] text-white transition-all cursor-pointer border-0 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="19" x2="12" y2="5" />
                <polyline points="5 12 12 5 19 12" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </form>
  );
}
