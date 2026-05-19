import { useChatContext } from "../context/ChatContext";
import { uploadDocuments } from "../api";

export function useUpload() {
  const { setMessages, setStatus } = useChatContext();

  async function handleUpload(files: FileList) {
    if (!files.length) {
      return;
    }

    setStatus("Uploading documents...");

    try {
      const response = await uploadDocuments(files);
      const fileList = response.files_processed.join(", ");

      setStatus(`Processing ${response.files_processed.length} file(s) in the background`);
      setMessages((current) => [
        ...current,
        {
          id: Date.now(),
          role: "system" as const,
          content: `Upload complete for: ${fileList}. Ingestion is running in the background; the knowledge base will refresh when processing finishes.`,
        },
      ]);
    } catch (error) {
      const message = error instanceof Error ? error.message : "Upload failed";
      setStatus(message);
      setMessages((current) => [
        ...current,
        {
          id: Date.now(),
          role: "system" as const,
          content: message,
        },
      ]);
    }
  }

  return {
    handleUpload,
  };
}
