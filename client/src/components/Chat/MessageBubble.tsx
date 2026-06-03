import ReactMarkdown from "react-markdown";
import type { Message } from "../../types";
import CitationCard from "./CitationCard";
import StreamingIndicator from "./StreamingIndicator";

interface MessageBubbleProps {
  message: Message;
  isStreaming?: boolean;
}

export default function MessageBubble({
  message,
  isStreaming = false,
}: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}
      data-testid={`message-${message.role}`}
    >
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-white border border-gray-200 text-gray-800"
        }`}
      >
        {!isUser && !message.content && isStreaming ? (
          <StreamingIndicator />
        ) : (
          <div className={`prose prose-sm max-w-none ${isUser ? "prose-invert" : ""}`}>
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        )}
        {!isUser && message.citations.length > 0 && (
          <CitationCard citations={message.citations} />
        )}
      </div>
    </div>
  );
}
