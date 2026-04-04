import sys
import os
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

# Add the project root to the Python path so we can import our backend config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.config import settings

def test_neo4j_connection() -> bool:
    """
    Tests the connection to the Neo4j AuraDB instance.
    """
    print(f"Attempting to connect to Neo4j at: {settings.NEO4J_URI}...")
    
    try:
        # Initialize the driver
        driver = GraphDatabase.driver(
            settings.NEO4J_URI, 
            auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD)
        )
        
        # Verify connectivity (this will throw an error if auth fails)
        driver.verify_connectivity()
        print("✅ SUCCESS: Connected to Neo4j AuraDB!")
        
        driver.close()
        return True
        
    except ServiceUnavailable as e:
        print("❌ ERROR: Could not connect to Neo4j. Check your URI.")
        print(f"Details: {e}")
        return False
    except Exception as e:
        print("❌ ERROR: Authentication failed or other issue.")
        print(f"Details: {e}")
        return False

if __name__ == "__main__":
    test_neo4j_connection()
    