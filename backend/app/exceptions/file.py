class FileException(Exception):
    """Base exception for file domain operations."""
    def __init__(self, message: str = "A file operation error occurred."):
        self.message = message
        super().__init__(self.message)


class FileNotFoundException(FileException):
    """Raised when a file record or physical file is not found."""
    def __init__(self, file_id: int):
        self.file_id = file_id
        super().__init__(f"File with ID {file_id} was not found.")


class InvalidFileExtensionException(FileException):
    """Raised when an uploaded file extension is not permitted."""
    def __init__(self, extension: str, allowed_extensions: set[str]):
        self.extension = extension
        self.allowed_extensions = allowed_extensions
        allowed_str = ", ".join(sorted(allowed_extensions))
        super().__init__(
            f"File extension '.{extension}' is not allowed. Allowed extensions: {allowed_str}."
        )


class FileTooLargeException(FileException):
    """Raised when an uploaded file exceeds maximum allowed size."""
    def __init__(self, size_bytes: int, max_bytes: int):
        self.size_bytes = size_bytes
        self.max_bytes = max_bytes
        max_mb = max_bytes / (1024 * 1024)
        size_mb = size_bytes / (1024 * 1024)
        super().__init__(
            f"File size ({size_mb:.2f} MB) exceeds maximum allowed limit of {max_mb:.2f} MB."
        )


class FileStorageException(FileException):
    """Raised when saving or deleting a file from disk fails."""
    def __init__(self, message: str = "Failed to store or delete file on storage system."):
        super().__init__(message)
