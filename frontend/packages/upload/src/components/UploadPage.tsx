import { useState } from "react";
import type { ChangeEvent, DragEvent } from "react";
import UploadDropzone from "./UploadDropzone";
import UploadFileList from "./UploadFileList";

const ALLOWED_EXTENSIONS = ["pdf", "docx", "txt"];

interface UploadPageProps {
  onUpload: (files: FileList) => void;
  status: string;
}

export default function UploadPage({ onUpload, status }: UploadPageProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const isUploading = status === "Uploading documents..." || status.includes("Processing");
  const isSuccess = status.startsWith("Uploaded") || status.startsWith("Successfully");
  const isError = status.includes("failed") || status.includes("Error");

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
      const ext = file.name.split(".").pop()?.toLowerCase();
      return ext ? ALLOWED_EXTENSIONS.includes(ext) : false;
    });
    setSelectedFiles(validFiles);
  };

  const handleUploadClick = () => {
    if (selectedFiles.length > 0 && !isUploading) {
      const dataTransfer = new DataTransfer();
      selectedFiles.forEach((file) => dataTransfer.items.add(file));
      onUpload(dataTransfer.files);
    }
  };

  const getButtonClasses = () => {
    const baseClasses = "w-full max-w-xs py-3 px-6 rounded-xl font-semibold text-white transition-all shadow-md flex items-center justify-center gap-2";
    if (selectedFiles.length === 0 || isUploading) {
      return `${baseClasses} bg-gray-300 cursor-not-allowed shadow-none`;
    }
    return `${baseClasses} bg-gradient-to-r from-violet-500 to-indigo-600 hover:opacity-90 hover:shadow-lg hover:-translate-y-0.5`;
  };

  const getStatusClasses = () => {
    if (isSuccess) return "text-green-700 bg-green-50";
    if (isError) return "text-red-700 bg-red-50";
    if (isUploading) return "text-indigo-700 bg-indigo-50";
    return "text-transparent";
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

        <UploadDropzone
          isDragging={isDragging}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onFileInput={handleFileInput}
        />

        <UploadFileList files={selectedFiles} />

        <div className="flex flex-col items-center w-full gap-4 mt-2">
          <button
            onClick={handleUploadClick}
            disabled={selectedFiles.length === 0 || isUploading}
            className={getButtonClasses()}
          >
            {isUploading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-2 h-5 w-5 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </>
            ) : (
              "Upload to Knowledge Base"
            )}
          </button>

          <div
            className={`text-sm text-center px-4 py-2 rounded-lg ${getStatusClasses()}`}
          >
            {status}
          </div>
        </div>
      </div>
    </main>
  );
}
