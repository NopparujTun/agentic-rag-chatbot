import { useState, useRef } from 'react';
import type { ChangeEvent, DragEvent } from 'react';

interface UploadPageProps {
  onUpload: (files: FileList) => void;
  status: string;
}

export default function UploadPage({ onUpload, status }: UploadPageProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const isUploading = status === 'Uploading documents...';
  const isSuccess = status.startsWith('Uploaded');
  const isError = status.includes('failed') || status.includes('Error');

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleFileInput = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFiles(e.target.files);
    }
  };

  const handleFiles = (files: FileList) => {
    const validFiles = Array.from(files).filter((file) => {
      const ext = file.name.split('.').pop()?.toLowerCase();
      return ext === 'pdf' || ext === 'docx' || ext === 'txt';
    });
    setSelectedFiles(validFiles);
  };

  const handleUploadClick = () => {
    if (selectedFiles.length > 0 && !isUploading) {
      // Create a new FileList-like object
      const dataTransfer = new DataTransfer();
      selectedFiles.forEach((file) => dataTransfer.items.add(file));
      onUpload(dataTransfer.files);
    }
  };

  return (
    <main className="flex-1 bg-[#fafafa] h-full flex flex-col items-center justify-center py-10 px-8 overflow-hidden">
      <div className="flex flex-col items-center gap-8 w-full max-w-2xl">
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="text-3xl font-bold text-[#111] tracking-tight">Upload Documents</h1>
          <p className="text-[#666] text-sm">
            Add PDF, DOCX, or TXT files to enrich the Knowledge Base.
          </p>
        </div>

        {/* Drag & Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`w-full p-10 border-2 border-dashed rounded-2xl flex flex-col items-center justify-center gap-4 transition-all cursor-pointer bg-white
            ${
              isDragging
                ? 'border-indigo-500 bg-indigo-50/50 scale-[1.02]'
                : 'border-gray-200 hover:border-indigo-300 hover:bg-gray-50'
            }
          `}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileInput}
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

        {/* Selected Files List */}
        {selectedFiles.length > 0 && (
          <div className="w-full flex flex-col gap-3">
            <h3 className="text-sm font-semibold text-gray-700">Selected Files</h3>
            <div className="flex flex-col gap-2 max-h-[200px] overflow-y-auto pr-2">
              {selectedFiles.map((file, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-white border border-gray-100 rounded-xl shadow-sm"
                >
                  <div className="flex items-center gap-3 overflow-hidden">
                    <div className="w-8 h-8 rounded bg-gray-50 flex items-center justify-center shrink-0">
                      📄
                    </div>
                    <span className="text-sm font-medium text-gray-700 truncate">
                      {file.name}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400 shrink-0">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Button & Status */}
        <div className="flex flex-col items-center w-full gap-4 mt-2">
          <button
            onClick={handleUploadClick}
            disabled={selectedFiles.length === 0 || isUploading}
            className={`w-full max-w-xs py-3 px-6 rounded-xl font-semibold text-white transition-all shadow-md flex items-center justify-center gap-2
              ${
                selectedFiles.length === 0 || isUploading
                  ? 'bg-gray-300 cursor-not-allowed shadow-none'
                  : 'bg-gradient-to-r from-violet-500 to-indigo-600 hover:opacity-90 hover:shadow-lg hover:-translate-y-0.5'
              }
            `}
          >
            {isUploading ? (
              <>
                <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </>
            ) : (
              'Upload to Knowledge Base'
            )}
          </button>
          
          <div className={`text-sm text-center px-4 py-2 rounded-lg ${
            isSuccess ? 'text-green-700 bg-green-50' : 
            isError ? 'text-red-700 bg-red-50' : 
            isUploading ? 'text-indigo-700 bg-indigo-50' : 
            'text-transparent'
          }`}>
            {status}
          </div>
        </div>
      </div>
    </main>
  );
}
