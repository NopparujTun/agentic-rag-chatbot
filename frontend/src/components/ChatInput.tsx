import { useRef } from "react";
import { InputBar } from "./ui/input-bar";

interface ChatInputProps {
  isSending: boolean;
  onSendMessage: (message: string) => void;
  onUploadDocuments: (files: FileList) => void;
}

export default function ChatInput({ isSending, onSendMessage, onUploadDocuments }: ChatInputProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = (message: { role: "user"; content: string }) => {
    onSendMessage(message.content);
  };

  const handleAttach = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      onUploadDocuments(event.target.files);
    }
    event.target.value = "";
  };

  return (
    <>
      <input
        ref={fileInputRef}
        className="hidden"
        type="file"
        accept="application/pdf,.pdf"
        multiple
        onChange={handleFileChange}
      />
      <InputBar
        status={isSending ? "streaming" : "ready"}
        onSend={handleSend}
        onStop={() => {}}
        onAttach={handleAttach}
        disabled={isSending}
        placeholder="Ask anything to start a new chat..."
        className="w-full max-w-2xl mx-auto"
      />
    </>
  );
}
