import { useState, useRef, useEffect } from "react";
import FileUpload from "./FileUpload";

interface ChatInputProps {
  onSend: (message: string) => void;
  onFileSelect: (file: File) => void;
  isStreaming: boolean;
  isUploading: boolean;
  onStop: () => void;
  uploadStatus: {
    fileName: string | null;
    error: string | null;
    success: boolean;
  } | null;
}

export default function ChatInput({
  onSend,
  onFileSelect,
  isStreaming,
  isUploading,
  onStop,
  uploadStatus,
}: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height =
        Math.min(textareaRef.current.scrollHeight, 200) + "px";
    }
  }, [input]);

  const handleSubmit = () => {
    if (input.trim() && !isStreaming) {
      onSend(input);
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white px-4 py-3" data-testid="chat-input-container">
      {uploadStatus && (uploadStatus.error || uploadStatus.success) && (
        <div
          className={`mb-2 rounded-lg px-3 py-2 text-sm ${
            uploadStatus.error
              ? "bg-red-50 text-red-700 border border-red-200"
              : "bg-green-50 text-green-700 border border-green-200"
          }`}
          data-testid="upload-status"
        >
          {uploadStatus.error
            ? `Upload failed: ${uploadStatus.error}`
            : `"${uploadStatus.fileName}" uploaded successfully`}
        </div>
      )}

      <div className="mx-auto max-w-3xl flex items-end gap-2 rounded-2xl border border-gray-300 bg-gray-50 px-3 py-2 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100">
        <FileUpload onFileSelect={onFileSelect} isUploading={isUploading} />

        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a legal question..."
          rows={1}
          className="flex-1 resize-none bg-transparent text-sm text-gray-800 placeholder-gray-400 outline-none"
          data-testid="chat-textarea"
        />

        {isStreaming ? (
          <button
            onClick={onStop}
            className="rounded-full bg-gray-800 p-2 text-white hover:bg-gray-700 transition-colors cursor-pointer"
            data-testid="stop-button"
            aria-label="Stop generating"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="currentColor"
            >
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!input.trim()}
            className="rounded-full bg-blue-600 p-2 text-white hover:bg-blue-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            data-testid="send-button"
            aria-label="Send message"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13" />
              <polygon points="22 2 15 22 11 13 2 9 22 2" />
            </svg>
          </button>
        )}
      </div>

      <p className="text-center text-xs text-gray-400 mt-2">
        LawyerGPT can make mistakes. Always verify legal advice with a
        qualified professional.
      </p>
    </div>
  );
}
