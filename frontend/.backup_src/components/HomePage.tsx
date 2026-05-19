import ChatInput from "./ChatInput";
import HeroSection from "./HeroSection";

interface HomePageProps {
  isSending: boolean;
  status: string;
  onSendMessage: (message: string) => void;
  onUploadDocuments: (files: FileList) => void;
}

export default function HomePage({
  isSending,
  status,
  onSendMessage,
  onUploadDocuments,
}: HomePageProps) {
  return (
    <main className="flex-1 bg-white h-full flex flex-col items-center justify-between py-6 px-4 md:px-8 overflow-hidden font-sans">
      <div className="flex flex-col items-center gap-6 flex-1 w-full justify-center">
        <HeroSection showDescription={true} />
      </div>

      <div className="w-full max-w-2xl">
        <p className="mb-2 text-center text-xs text-[#777]">{status}</p>
        <ChatInput
          isSending={isSending}
          onSendMessage={onSendMessage}
          onUploadDocuments={onUploadDocuments}
        />
      </div>
    </main>
  );
}
