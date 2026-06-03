import { useState, useCallback, useRef } from "react";
import { v4 as uuidv4 } from "uuid";
import type { Message, Citation, ModelId } from "../types";
import { streamChat } from "../services/api";

interface UseChatParams {
  activeId: string | null;
  addMessage: (conversationId: string, message: Message) => void;
  updateLastAssistantMessage: (
    conversationId: string,
    updater: (msg: Message) => Message
  ) => void;
  updateConversationTitle: (id: string, title: string) => void;
  activeMessages: Message[];
  createConversation: () => Promise<string>;
  selectedModel: ModelId;
}

export function useChat({
  activeId,
  addMessage,
  updateLastAssistantMessage,
  updateConversationTitle,
  activeMessages,
  createConversation,
  selectedModel,
}: UseChatParams) {
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed) return;

      let convId = activeId;
      if (!convId) {
        convId = await createConversation();
      }

      const userMsg: Message = {
        id: uuidv4(),
        conversation_id: convId,
        role: "user",
        content: trimmed,
        citations: [],
        created_at: new Date().toISOString(),
      };
      addMessage(convId, userMsg);

      if (activeMessages.length === 0) {
        const title =
          trimmed.length > 40 ? trimmed.substring(0, 40) + "..." : trimmed;
        updateConversationTitle(convId, title);
      }

      const assistantMsg: Message = {
        id: uuidv4(),
        conversation_id: convId,
        role: "assistant",
        content: "",
        citations: [],
        created_at: new Date().toISOString(),
      };
      addMessage(convId, assistantMsg);
      setIsStreaming(true);

      const capturedConvId = convId;

      abortRef.current = streamChat(
        capturedConvId,
        trimmed,
        selectedModel,
        (token) => {
          updateLastAssistantMessage(capturedConvId, (msg) => ({
            ...msg,
            content: msg.content + token,
          }));
        },
        (citationsJson) => {
          try {
            const citations: Citation[] = JSON.parse(citationsJson);
            updateLastAssistantMessage(capturedConvId, (msg) => ({
              ...msg,
              citations,
            }));
          } catch {
            // ignore parse errors
          }
        },
        () => {
          setIsStreaming(false);
          abortRef.current = null;
        },
        (error) => {
          updateLastAssistantMessage(capturedConvId, (msg) => ({
            ...msg,
            content:
              msg.content ||
              `Sorry, an error occurred: ${error}. The backend server may not be running yet.`,
          }));
          setIsStreaming(false);
          abortRef.current = null;
        }
      );
    },
    [
      activeId,
      addMessage,
      updateLastAssistantMessage,
      updateConversationTitle,
      activeMessages,
      createConversation,
      selectedModel,
    ]
  );

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    setIsStreaming(false);
    abortRef.current = null;
  }, []);

  return { isStreaming, sendMessage, stopStreaming };
}
