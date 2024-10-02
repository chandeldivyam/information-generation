import os
from typing import List, Union
from urllib.parse import urlparse

from langchain_community.document_loaders import (
    CSVLoader,
    PyPDFLoader,
    TextLoader,
)
from langchain.schema import Document

def load_document(source: str) -> List[Document]:
    """
    Load a document from a file path or public URL.

    Args:
        source (str): The file path or public URL of the document.

    Returns:
        List[Document]: A list of LangChain Document objects.

    Raises:
        ValueError: If the file extension is not supported or the source is invalid.
    """
    # Determine if the source is a URL or a file path
    parsed_url = urlparse(source)
    is_url = bool(parsed_url.scheme and parsed_url.netloc)

    if is_url:
        # For URLs, we'll need to download the file first
        # This is a placeholder - you'll need to implement file downloading logic
        raise NotImplementedError("URL handling not implemented yet")
    else:
        # For file paths, check if the file exists
        if not os.path.exists(source):
            raise ValueError(f"File not found: {source}")

    # Get the file extension
    _, file_extension = os.path.splitext(source)
    file_extension = file_extension.lower()

    # Choose the appropriate loader based on the file extension
    if file_extension == '.csv':
        loader = CSVLoader(source)
    elif file_extension == '.pdf':
        loader = PyPDFLoader(source)
    elif file_extension in ['.txt', '.md']:
        loader = TextLoader(source)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    # Load the document
    return loader.load()