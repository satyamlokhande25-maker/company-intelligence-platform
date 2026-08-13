def chunk_documents(documents: list[dict], chunk_size: int = 250, overlap: int = 40) -> list[dict]:
    """
    Splits document texts into smaller, overlapping chunks for embedding creation.
    """
    chunks = []

    for doc in documents:
        text = doc["text"]
        metadata = doc["metadata"]
        words = text.split()

        if len(words) <= chunk_size:
            chunks.append({"text": text, "metadata": metadata})
            continue

        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i : i + chunk_size]
            chunk_text = " ".join(chunk_words)
            chunks.append({"text": chunk_text, "metadata": metadata})

    return chunks