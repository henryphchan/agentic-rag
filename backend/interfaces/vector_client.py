from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseVectorClient(ABC):
    """
    Abstract base class defining the contract for Vector Database operations.
    """

    @abstractmethod
    def search(self, collection_name: str, query_vector: List[float], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Performs a semantic similarity search in the vector database.

        Args:
            collection_name (str): The name of the collection to search.
            query_vector (List[float]): The vectorized representation of the search query.
            limit (int, optional): The maximum number of results to return. Defaults to 5.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing the retrieved payload and score.
        """
        pass

    @abstractmethod
    def create_collection_if_not_exists(self, collection_name: str, vector_size: int) -> None:
        """Ensures the target vector collection exists before inserting data."""
        pass

    @abstractmethod
    def upsert(self, collection_name: str, vector: List[float], payload: Dict[str, Any], point_id: str) -> None:
        """Inserts a vector and its associated metadata into the database."""
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        """
        Deletes a vector collection and all its associated data.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        pass
    