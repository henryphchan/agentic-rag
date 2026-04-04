from typing import Dict, Any
from langchain_core.tools import tool
from backend.services.neo4j_service import Neo4jService

@tool
def execute_graph_query(cypher_query: str) -> str:
    """
    Executes a Cypher query against the Neo4j graph database to find relationships between entities.
    Use this tool strictly when you need to understand how people, organizations, or concepts are structurally connected.

    CRITICAL GRAPH SCHEMA RULES:
    1. Every single node in the database uses the generic label `Entity`. 
    2. Example of a correct query: MATCH (s:Entity {name: 'StellarTech'})-[r]->(t:Entity) RETURN s, type(r), t

    Args:
        cypher_query (str): A valid Neo4j Cypher query following the schema rules above.

    Returns:
        str: A string representation of the graph records found.
    """
    neo4j = Neo4jService()
    try:
        results = neo4j.execute_query(cypher_query)
        neo4j.close()
        
        if not results:
            return "No graph relationships found for this query."
            
        # Convert the dictionary results into a string format the LLM can read
        return str(results)
        
    except Exception as e:
        neo4j.close()
        # Returning the error to the LLM allows it to self-correct and try a different query
        return f"Error executing Cypher query. Check your syntax. Details: {str(e)}"
        