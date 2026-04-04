def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits a large string of text into smaller, overlapping chunks.

    Args:
        text (str): The raw input text to be chunked.
        chunk_size (int, optional): The maximum number of characters per chunk. Defaults to 500.
        overlap (int, optional): The number of characters to overlap between chunks 
            to preserve semantic context. Defaults to 50.

    Returns:
        list[str]: A list of text chunks.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks
    