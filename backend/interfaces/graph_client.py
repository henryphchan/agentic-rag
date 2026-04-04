from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseGraphClient(ABC):
    """
    Abstract base class defining the contract for Graph Database operations.
    """

    @abstractmethod
    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Executes a query against the graph database and returns the results.

        Args:
            query (str): The graph query string (e.g., Cypher).
            parameters (Dict[str, Any], optional): Parameters to inject into the query. Defaults to None.

        Returns:
            List[Dict[str, Any]]: A list of records returned by the database.
        """
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str) -> None:
        """
        Deletes the specified collection from the graph database.

        Args:
            collection_name (str): The name of the collection to delete.
        """
        pass
    