import sys
import os
import subprocess

# Ensure the backend module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.neo4j_service import Neo4jService
from backend.services.qdrant_service import QdrantService
from data_pipeline.cleanup_dbs import wipe_databases

def test_sample_pipeline():
    """
    End-to-End integration test for the ETL pipeline.
    It wipes the databases, runs the pipeline on sample text, and verifies ingestion.
    """
    # 1. Start with a clean slate
    wipe_databases()
    
    # 2. Run the pipeline orchestrator via a subprocess
    sample_file_path = "tests/sample_data/sample.txt"
    print(f"\n🚀 Running Pipeline Test on {sample_file_path}...")
    
    # This runs exactly what you would type into the terminal
    result = subprocess.run(
        ["python", "data_pipeline/run_pipeline.py", "--file", sample_file_path],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("❌ Pipeline failed to execute. Error logs:")
        print(result.stderr)
        return
        
    print("✅ Pipeline executed successfully. Verifying data landing...")
    
    # 3. Verify Graph Data
    neo4j = Neo4jService()
    node_count = neo4j.execute_query("MATCH (n) RETURN count(n) as count")[0]["count"]
    edge_count = neo4j.execute_query("MATCH ()-[r]->() RETURN count(r) as count")[0]["count"]
    neo4j.close()
    
    print(f"  -> Neo4j Status: Found {node_count} nodes and {edge_count} relationships.")
    
    # 4. Verify Vector Data
    qdrant = QdrantService()
    try:
        collection_info = qdrant.client.get_collection("research_documents")
        vector_count = collection_info.points_count
        print(f"  -> Qdrant Status: Found {vector_count} vectors.")
    except Exception as e:
        print(f"  -> Qdrant Error: {e}")
        vector_count = 0
        
    # 5. Final Assertion
    if node_count > 0 and vector_count > 0:
        print("\n🎉 INTEGRATION TEST PASSED! Data successfully ingested into both databases.")
    else:
        print("\n❌ INTEGRATION TEST FAILED! Databases are missing data.")

if __name__ == "__main__":
    test_sample_pipeline()
    
    