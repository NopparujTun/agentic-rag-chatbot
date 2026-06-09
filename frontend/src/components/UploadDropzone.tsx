import { useRef } from "react";
import type { ChangeEvent, DragEvent } from "react";

interface UploadDropzoneProps {
  isDragging: boolean;
  onDragOver: (e: DragEvent<HTMLDivElement>) => void;
  onDragLeave: (e: DragEvent<HTMLDivElement>) => void;
  onDrop: (e: DragEvent<HTMLDivElement>) => void;
  onFileInput: (e: ChangeEvent<HTMLInputElement>) => void;
}

export default function UploadDropzone({
  isDragging,
  onDragOver,
  onDragLeave,
  onDrop,
  onFileInput,
}: UploadDropzoneProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  return (
    <div
      onDragOver={onDragOver}
      onDragLeave={onDragLeave}
      onDrop={onDrop}
      onClick={() => fileInputRef.current?.click()}
      className={`w-full p-10 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center gap-4 transition-all cursor-pointer bg-white
        ${
          isDragging
            ? "border-indigo-500 bg-indigo-50/50 scale-[1.02]"
            : "border-gray-200 hover:border-indigo-300 hover:bg-gray-50"
        }
      `}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={onFileInput}
        className="hidden"
        multiple
        accept=".pdf,.docx,.txt"
      />
      <div className="w-16 h-16 rounded-full bg-indigo-50 flex items-center justify-center mb-2">
        <svg
          className="w-8 h-8 text-indigo-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
          />
        </svg>
      </div>
      <div className="text-center">
        <span className="font-semibold text-indigo-600">Click to upload</span> or drag and drop
        <p className="text-xs text-gray-400 mt-1">Supported formats: PDF, DOCX, TXT</p>
      </div>
    </div>
  );
}
