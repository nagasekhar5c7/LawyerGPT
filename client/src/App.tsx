import { useEffect, useState } from "react";
import AppLayout from "./components/Layout/AppLayout";
import Sidebar from "./components/Sidebar/Sidebar";
import ChatArea from "./components/Chat/ChatArea";
import ChatInput from "./components/Input/ChatInput";
import ModelSelector from "./components/Layout/ModelSelector";
import { useConversations } from "./hooks/useConversations";
import { useChat } from "./hooks/useChat";
import { useFileUpload } from "./hooks/useFileUpload";
import { DEFAULT_MODEL } from "./types";
import type { ModelId } from "./types";

export default function App() {
  const {
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
  } = useConversations();

  const [selectedModel, setSelectedModel] = useState<ModelId>(DEFAULT_MODEL);

  const { isStreaming, sendMessage, stopStreaming } = useChat({
    activeId,
    addMessage,
    updateLastAssistantMessage,
    updateConversationTitle,
    activeMessages,
    createConversation,
    selectedModel,
  });

  const { uploadState, uploadFile, clearUploadState } = useFileUpload();

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    if (uploadState.success || uploadState.error) {
      const timer = setTimeout(clearUploadState, 5000);
      return () => clearTimeout(timer);
    }
  }, [uploadState.success, uploadState.error, clearUploadState]);

  return (
    <AppLayout
      sidebar={
        <Sidebar
          conversations={conversations}
          activeId={activeId}
          onNewChat={createConversation}
          onSelect={selectConversation}
          onDelete={removeConversation}
        />
      }
    >
      <div className="flex flex-col h-full">
        <header className="flex items-center justify-between border-b border-gray-200 bg-white px-6 py-3">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold text-gray-800">LawyerGPT</h1>
            <ModelSelector
              selectedModel={selectedModel}
              onModelChange={setSelectedModel}
            />
          </div>
          <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">
            Legal AI Assistant
          </span>
        </header>

        <ChatArea messages={activeMessages} isStreaming={isStreaming} />

        <ChatInput
          onSend={sendMessage}
          onFileSelect={uploadFile}
          isStreaming={isStreaming}
          isUploading={uploadState.isUploading}
          onStop={stopStreaming}
          uploadStatus={
            uploadState.error || uploadState.success
              ? {
                  fileName: uploadState.fileName,
                  error: uploadState.error,
                  success: uploadState.success,
                }
              : null
          }
        />
      </div>
    </AppLayout>
  );
}
