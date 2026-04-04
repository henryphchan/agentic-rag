from typing import Any, Dict, List
from neo4j import GraphDatabase
from backend.interfaces.graph_client import BaseGraphClient
from backend.core.config import settings

class Neo4jService(BaseGraphClient):
    """
    Concrete implementation of BaseGraphClient using the Neo4j Python driver.
    """

    def __init__(self):
        self._driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )

    def close(self):
        """Closes the connection to the Neo4j database."""
        if self._driver:
            self._driver.close()

    def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Executes a Cypher query against Neo4j AuraDB.

        Args:
            query (str): The Cypher query string.
            parameters (Dict[str, Any], optional): Dictionary of parameters. Defaults to None.

        Returns:
            List[Dict[str, Any]]: The records retrieved from the database.
        """
        parameters = parameters or {}
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [record.data() for record in result]

    def delete_collection(self, collection_name: str) -> None:
        """
        Deletes the specified collection from Neo4j.
        """
        # We use a Cypher query to delete the collection
        query = f"MATCH (n) WHERE n:ResearchDocument DELETE n"
        self.execute_query(query)
        