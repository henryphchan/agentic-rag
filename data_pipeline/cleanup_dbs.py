import sys
import os

# Ensure the backend module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.neo4j_service import Neo4jService
from backend.services.qdrant_service import QdrantService

def wipe_databases():
    """
    Cleans all data from the Neo4j graph and drops the Qdrant vector collection.
    """
    print("Starting Database Cleanup...")
    
    # 1. Clean Neo4j Graph
    print("  -> Wiping Neo4j Graph...")
    neo4j = Neo4jService()
    # DETACH DELETE removes all nodes and their relationships
    neo4j.execute_query("MATCH (n) DETACH DELETE n")
    neo4j.close()
    
    # 2. Clean Qdrant Vectors
    print("  -> Dropping Qdrant Collection 'research_documents'...")
    qdrant = QdrantService()
    qdrant.delete_collection("research_documents")
    
    print("✅ Cleanup Complete! Databases are fresh and empty.")

if __name__ == "__main__":
    wipe_databases()
