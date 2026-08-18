import logging
from pathlib import Path
from typing import Union
from langchain_community.document_loaders import PyPDFLoader, TextLoader

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: Union[str, Path], extension: str = "") -> str:
    """
    Extract text content from a file using LangChain document loaders.
    
    - For PDF files (.pdf): Uses LangChain's PyPDFLoader to parse document pages.
    - For text files (.txt): Uses LangChain's TextLoader or UTF-8 reading.
    - Fallback: Attempts reading text content for other extensions.
    
    :param file_path: Path object or string path to physical file on disk.
    :param extension: Lowercase extension string (e.g., 'pdf', 'txt').
    :return: Extracted text string.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found at path: {path}")

    ext = (extension or path.suffix.lstrip(".")).lower().strip()

    if ext == "pdf":
        logger.info(f"Loading PDF document using LangChain PyPDFLoader: {path}")
        loader = PyPDFLoader(str(path))
        docs = loader.load()
        extracted_pages = [doc.page_content for doc in docs if doc.page_content]
        extracted_text = "\n\n".join(extracted_pages).strip()
        if not extracted_text:
            logger.warning(f"PyPDFLoader extracted empty text from PDF: {path}")
        return extracted_text

    elif ext == "txt":
        logger.info(f"Loading text document using LangChain TextLoader: {path}")
        try:
            loader = TextLoader(str(path), encoding="utf-8")
            docs = loader.load()
            return "\n\n".join([doc.page_content for doc in docs]).strip()
        except Exception as err:
            logger.warning(f"TextLoader failed for {path}: {err}. Falling back to direct read.")
            return path.read_text(encoding="utf-8", errors="ignore").strip()

    else:
        logger.info(f"Extracting raw text from fallback file extension '.{ext}': {path}")
        try:
            return path.read_text(encoding="utf-8", errors="ignore").strip()
        except Exception as exc:
            raise ValueError(f"Unsupported file format '.{ext}' or binary content in {path}: {exc}") from exc
