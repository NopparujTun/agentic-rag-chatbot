

interface UploadFileListProps {
  files: File[];
}

export default function UploadFileList({ files }: UploadFileListProps) {
  if (files.length === 0) return null;

  return (
    <div className="w-full flex flex-col gap-3">
      <h3 className="text-sm font-semibold text-gray-700">Selected Files</h3>
      <div className="flex flex-col gap-2 max-h-[200px] overflow-y-auto pr-2">
        {files.map((file, idx) => (
          <div
            key={idx}
            className="flex items-center justify-between p-3 bg-white border border-gray-100 rounded-xl shadow-sm"
          >
            <div className="flex items-center gap-3 overflow-hidden">
              <div className="w-8 h-8 rounded bg-gray-50 flex items-center justify-center shrink-0">
                📄
              </div>
              <span className="text-sm font-medium text-gray-700 truncate">{file.name}</span>
            </div>
            <span className="text-xs text-gray-400 shrink-0">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
