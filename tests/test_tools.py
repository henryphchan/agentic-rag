import sys
import os

# Ensure the backend module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.tools.semantic_search import search_knowledge_base
from backend.tools.cypher_generator import execute_graph_query

def run_tool_tests():
    """
    Manually tests the LangChain tools to ensure they correctly interact 
    with the Vector and Graph databases.
    """
    print("🚀 Starting Tool Isolation Tests...\n")
    
    # ---------------------------------------------------------
    # Test 1: Semantic Vector Search
    # ---------------------------------------------------------
    print("--- Test 1: Vector Search Tool ---")
    vector_query = {"query": "What is Project Obsidian and who leads it?"}
    print(f"Querying Qdrant for: '{vector_query['query']}'")
    
    vector_result = search_knowledge_base.invoke(vector_query)
    print("\nVector Result Payload:")
    print(vector_result)
    print("-" * 50 + "\n")

    # ---------------------------------------------------------
    # Test 2: Graph Cypher Execution
    # ---------------------------------------------------------
    print("--- Test 2: Graph Execution Tool ---")
    # A Cypher query to find out who StellarTech acquired
    graph_query = {
        "cypher_query": "MATCH (s:Entity {name: 'StellarTech'})-[r:ACQUIRED]->(target) RETURN s.name, type(r), target.name"
    }
    print(f"Executing Cypher against Neo4j:\n{graph_query['cypher_query']}")
    
    graph_result = execute_graph_query.invoke(graph_query)
    print("\nGraph Result Payload:")
    print(graph_result)
    print("-" * 50 + "\n")
    
    print("✅ Tool Isolation Tests Complete!")

if __name__ == "__main__":
    run_tool_tests()

