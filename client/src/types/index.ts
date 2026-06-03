export interface Citation {
  document_name: string;
  page_number: number;
  chunk_text: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  citations: Citation[];
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

export interface DocumentInfo {
  id: string;
  filename: string;
  file_size: number;
  total_chunks: number;
  status: "processing" | "completed" | "failed";
  created_at: string;
}

export const AVAILABLE_MODELS = [
  { id: "gpt-5.5", name: "GPT-5.5", provider: "OpenAI" },
  { id: "gpt-4o", name: "GPT-4o", provider: "OpenAI" },
  { id: "gpt-4o-mini", name: "GPT-4o Mini", provider: "OpenAI" },
  { id: "claude-sonnet-4-6", name: "Claude Sonnet 4.6", provider: "Anthropic" },
  { id: "claude-haiku-4-5", name: "Claude Haiku 4.5", provider: "Anthropic" },
] as const;

export type ModelId = (typeof AVAILABLE_MODELS)[number]["id"];

export const DEFAULT_MODEL: ModelId = "gpt-5.5";

export interface ChatRequest {
  message: string;
  model: ModelId;
}

export interface SSEEvent {
  type: "token" | "citations" | "done" | "error";
  data: string;
}
