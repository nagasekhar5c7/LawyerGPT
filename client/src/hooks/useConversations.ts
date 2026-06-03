import { useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import type { Conversation, Message } from "../types";
import * as api from "../services/api";

export function useConversations() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messagesMap, setMessagesMap] = useState<Record<string, Message[]>>({});

  const loadConversations = useCallback(async () => {
    try {
      const data = await api.listConversations();
      setConversations(data);
    } catch {
      // Backend not available yet — use local state
    }
  }, []);

  const createConversation = useCallback(async (): Promise<string> => {
    try {
      const conv = await api.createConversation();
      setConversations((prev) => [conv, ...prev]);
      setMessagesMap((prev) => ({ ...prev, [conv.id]: [] }));
      setActiveId(conv.id);
      return conv.id;
    } catch {
      const id = uuidv4();
      const conv: Conversation = {
        id,
        title: "New Chat",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setConversations((prev) => [conv, ...prev]);
      setMessagesMap((prev) => ({ ...prev, [id]: [] }));
      setActiveId(id);
      return id;
    }
  }, []);

  const selectConversation = useCallback(
    async (id: string) => {
      setActiveId(id);
      if (messagesMap[id]) return;
      try {
        const conv = await api.getConversation(id);
        setMessagesMap((prev) => ({ ...prev, [id]: conv.messages }));
      } catch {
        setMessagesMap((prev) => ({ ...prev, [id]: [] }));
      }
    },
    [messagesMap]
  );

  const removeConversation = useCallback(
    async (id: string) => {
      try {
        await api.deleteConversation(id);
      } catch {
        // offline delete
      }
      setConversations((prev) => prev.filter((c) => c.id !== id));
      setMessagesMap((prev) => {
        const copy = { ...prev };
        delete copy[id];
        return copy;
      });
      if (activeId === id) setActiveId(null);
    },
    [activeId]
  );

  const addMessage = useCallback((conversationId: string, message: Message) => {
    setMessagesMap((prev) => ({
      ...prev,
      [conversationId]: [...(prev[conversationId] || []), message],
    }));
  }, []);

  const updateLastAssistantMessage = useCallback(
    (conversationId: string, updater: (msg: Message) => Message) => {
      setMessagesMap((prev) => {
        const msgs = [...(prev[conversationId] || [])];
        for (let i = msgs.length - 1; i >= 0; i--) {
          if (msgs[i].role === "assistant") {
            msgs[i] = updater(msgs[i]);
            break;
          }
        }
        return { ...prev, [conversationId]: msgs };
      });
    },
    []
  );

  const updateConversationTitle = useCallback(
    (id: string, title: string) => {
      setConversations((prev) =>
        prev.map((c) => (c.id === id ? { ...c, title } : c))
      );
    },
    []
  );

  const activeMessages = activeId ? messagesMap[activeId] || [] : [];

  return {
    conversations,
    activeId,
    activeMessages,
    loadConversations,
    createConversation,
    selectConversation,
    removeConversation,
    addMessage,
    updateLastAssistantMessage,
    updateConversationTitle,
  };
}
