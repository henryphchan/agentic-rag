import requests
from typing import Dict, Any
from langchain_core.tools import tool
from backend.services.qdrant_service import QdrantService
from backend.core.config import settings

@tool
def search_knowledge_base(query: str) -> str:
    """
    Searches the vector database for unstructured text context related to the query.
    Use this tool when you need to find general information, definitions, or semantic context.

    Args:
        query (str): The specific question or search term.

    Returns:
        str: The retrieved text context from the knowledge base.
    """
    # 1. Generate the embedding via the local Ollama API
    url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
    payload = {
        "model": settings.EMBEDDING_MODEL,
        "prompt": query
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        vector = response.json().get("embedding", [])
    except requests.exceptions.RequestException as e:
        return f"System error generating embedding: {str(e)}"
    
    # 2. Search Qdrant
    qdrant = QdrantService()
    try:
        results = qdrant.search(
            collection_name="research_documents", 
            query_vector=vector, 
            limit=3
        )
        
        # 3. Format the payload text back to the LLM
        if not results:
            return "No relevant context found in the knowledge base."
        
        # Join the text chunks together with a visual separator
        context = "\n\n---\n\n".join([hit.get("text", "") for hit in results])
        return context
        
    except Exception as e:
        return f"System error searching vector database: {str(e)}"


