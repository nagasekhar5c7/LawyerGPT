class LawyerGPTError(Exception):
    def __init__(self, message: str, error_code: str = "INTERNAL_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)


class ConversationNotFoundError(LawyerGPTError):
    def __init__(self, conversation_id: str):
        super().__init__(
            message=f"Conversation not found: {conversation_id}",
            error_code="CONVERSATION_NOT_FOUND",
        )


class DocumentProcessingError(LawyerGPTError):
    def __init__(self, message: str):
        super().__init__(message=message, error_code="DOCUMENT_PROCESSING_ERROR")


class LLMError(LawyerGPTError):
    def __init__(self, message: str):
        super().__init__(message=message, error_code="LLM_ERROR")


class RetrievalError(LawyerGPTError):
    def __init__(self, message: str):
        super().__init__(message=message, error_code="RETRIEVAL_ERROR")
