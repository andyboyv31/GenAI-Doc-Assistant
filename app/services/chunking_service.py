import re


def create_text_chunks(text: str, chunk_size: int = 500, overlap: int = 100):
    """
    Split cleaned document text into smaller overlapping chunks.
    """

    if not text or not text.strip():
        return []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks


def semantic_chunk_text(text: str):
    """
    Split text based on sentence boundaries.
    This supports semantic boundary chunking.
    """

    if not text or not text.strip():
        return []

    sentences = re.split(r'(?<=[.!?])\s+', text)

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]