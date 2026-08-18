class ChatException(Exception):
    """Base exception for chat domain operations."""
    def __init__(self, message: str = "A chat operation error occurred."):
        self.message = message
        super().__init__(self.message)


class ChatNotFoundException(ChatException):
    """Raised when a chat session is not found."""
    def __init__(self, chat_id: int):
        self.chat_id = chat_id
        super().__init__(f"Chat session with ID {chat_id} was not found.")


class ChatMessageException(ChatException):
    """Raised when a chat message input is invalid."""
    def __init__(self, message: str = "Invalid message provided."):
        super().__init__(message)


class LLMProcessingException(ChatException):
    """Raised when an error occurs during LLM execution or parsing."""
    def __init__(self, message: str = "Error encountered during LLM message processing."):
        super().__init__(message)
