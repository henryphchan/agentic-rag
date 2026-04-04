import sys
import os
from qdrant_client import QdrantClient

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.config import settings

def test_qdrant_connection() -> bool:
    """
    Tests the connection to the Qdrant Cloud cluster.
    """
    print(f"Attempting to connect to Qdrant at: {settings.QDRANT_URL}...")
    
    try:
        # Initialize the client
        client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )
        
        # Ping the database by requesting collections
        collections = client.get_collections()
        
        print("✅ SUCCESS: Connected to Qdrant Cloud!")
        print(f"Existing Collections: {collections.collections}")
        return True
        
    except Exception as e:
        print("❌ ERROR: Could not connect to Qdrant. Check your URL and API Key.")
        print(f"Details: {e}")
        return False

if __name__ == "__main__":
    test_qdrant_connection()
    