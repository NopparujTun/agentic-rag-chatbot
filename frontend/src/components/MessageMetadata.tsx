import type { ChatResponse } from '../api';

interface MessageMetadataProps {
  metadata: ChatResponse;
}

export default function MessageMetadata({ metadata }: MessageMetadataProps) {
  if (!metadata.steps?.length && !metadata.sources?.length) {
    return null;
  }

  return (
    <div className="flex flex-col gap-2 w-full mt-2">
      {metadata.steps && metadata.steps.length > 0 && (
        <details className="mt-1 text-xs text-gray-600 border border-gray-200 rounded-xl overflow-hidden w-full bg-white shadow-sm hover:shadow transition-shadow">
          <summary className="cursor-pointer font-medium px-4 py-2 bg-gray-50 hover:bg-gray-100 transition-colors">
            🧠 Thought Process ({metadata.steps.length} steps)
          </summary>
          <div className="p-3 bg-white flex flex-col gap-3 max-h-60 overflow-y-auto border-t border-gray-100">
            {metadata.steps.map((step, idx) => (
              <div key={idx} className="flex flex-col gap-1 border-b border-gray-50 pb-2 last:border-0 last:pb-0">
                <div className="font-semibold text-gray-700">🛠️ Tool: {step.tool}</div>
                <div className="text-gray-500 bg-gray-50 p-1.5 rounded-md font-mono text-[10px]">Input: {JSON.stringify(step.tool_input)}</div>
                <div className="text-gray-600 bg-blue-50/50 p-1.5 rounded-md truncate" title={step.observation}>
                  Result: {step.observation.length > 100 ? step.observation.substring(0, 100) + '...' : step.observation}
                </div>
              </div>
            ))}
          </div>
        </details>
      )}

      {metadata.sources && metadata.sources.length > 0 && (
        <details className="mt-1 text-xs text-gray-600 border border-gray-200 rounded-xl overflow-hidden w-full bg-white shadow-sm hover:shadow transition-shadow">
          <summary className="cursor-pointer font-medium px-4 py-2 bg-gray-50 hover:bg-gray-100 transition-colors">
            📚 Sources ({metadata.sources.length})
          </summary>
          <div className="p-3 bg-white flex flex-col gap-3 max-h-60 overflow-y-auto border-t border-gray-100">
            {metadata.sources.map((source, idx) => (
              <div key={idx} className="flex flex-col gap-1 border border-gray-100 rounded-lg p-2.5 bg-gray-50">
                <div className="font-semibold text-gray-800 truncate" title={source.metadata?.source || 'Unknown file'}>
                  📄 {source.metadata?.source?.split('/').pop() || source.metadata?.source?.split('\\').pop() || 'Unknown file'}
                </div>
                <div className="text-gray-500 line-clamp-3 leading-relaxed mt-1">{source.content}</div>
              </div>
            ))}
          </div>
        </details>
      )}
    </div>
  );
}
