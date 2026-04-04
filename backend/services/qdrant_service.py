from typing import Any, Dict, List
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from backend.interfaces.vector_client import BaseVectorClient
from backend.core.config import settings

class QdrantService(BaseVectorClient):
    """
    Concrete implementation of BaseVectorClient using the Qdrant Cloud client.
    """

    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY
        )

    def create_collection_if_not_exists(self, collection_name: str, vector_size: int = 768) -> None:
        """
        Checks if a collection exists, and creates it if it does not.
        Note: nomic-embed-text outputs a vector size of 768.
        """
        if not self.client.collection_exists(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )

    def upsert(self, collection_name: str, vector: List[float], payload: Dict[str, Any], point_id: str) -> None:
        """
        Upserts a single vector and its text payload into Qdrant.
        """
        point = PointStruct(
            id=point_id, 
            vector=vector, 
            payload=payload
        )
        self.client.upsert(
            collection_name=collection_name,
            points=[point]
        )

    def search(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Searches Qdrant for vectors semantically similar to the query vector.

        Args:
            collection_name (str): The target Qdrant collection.
            query_vector (List[float]): The embedding vector to search with.
            limit (int, optional): Maximum results to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the matched payload.
        """
        # Qdrant v1.10.0+ uses query_points instead of the deprecated search method
        search_result = self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit
        )
        
        # Extract the payload (the actual text data) from the result points
        return [hit.payload for hit in search_result.points]

    def delete_collection(self, collection_name: str) -> None:
        """
        Deletes the specified collection from Qdrant.
        """
        if self.client.collection_exists(collection_name):
            self.client.delete_collection(collection_name=collection_name)
            