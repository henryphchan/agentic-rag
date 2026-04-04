import requests
from backend.core.config import settings

def generate_embedding(text: str) -> list[float]:
    """
    Generates a vector embedding for a given string using the local embedding model.

    Args:
        text (str): The text to embed.

    Returns:
        list[float]: The resulting vector representation.
    """
    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model": settings.EMBEDDING_MODEL,
        "prompt": text
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        return response.json().get("embedding", [])
    else:
        raise RuntimeError(f"Embedding generation failed: {response.text}")
        