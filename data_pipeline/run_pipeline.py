import sys
import os
import argparse
import hashlib
import re

# Ensure the backend module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ollama_client import OllamaClient
from backend.services.neo4j_service import Neo4jService
from backend.services.qdrant_service import QdrantService
from data_pipeline.transformers.chunker import chunk_text
from data_pipeline.transformers.graph_extractor import extract_entities_and_relationships
from data_pipeline.transformers.embedder import generate_embedding

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Agentic RAG ETL Pipeline.")
    parser.add_argument("--file", type=str, required=True, help="Path to the text file you want to process.")
    return parser.parse_args()

def main():
    args = parse_arguments()
    raw_file_path = args.file

    if not os.path.exists(raw_file_path):
        print(f"❌ Error: The file {raw_file_path} does not exist.")
        sys.exit(1)

    print(f"Starting ETL Pipeline for: {raw_file_path}")

    # 1. Instantiate Concrete Services
    llm = OllamaClient()
    neo4j = Neo4jService()
    qdrant = QdrantService()
    
    collection_name = "research_documents"
    
    print("Initializing databases...")
    # nomic-embed-text generates 768-dimensional vectors
    qdrant.create_collection_if_not_exists(collection_name, vector_size=768)
    
    # 2. Load Raw Data
    with open(raw_file_path, 'r', encoding='utf-8') as file:
        raw_text = file.read()

    # 3. Process Text
    chunks = chunk_text(raw_text)
    print(f"Generated {len(chunks)} chunks.")

    for i, chunk in enumerate(chunks):
        print(f"\nProcessing Chunk {i+1}/{len(chunks)}...")
        
        # --- VECTOR PIPELINE ---
        print("  -> Generating vector embedding...")
        vector = generate_embedding(chunk)
        
        print("  -> Loading to Qdrant...")
        # Create a unique ID and structure the payload
        point_id = hashlib.md5(chunk.encode('utf-8')).hexdigest()
        payload = {
            "text": chunk,
            "source_file": os.path.basename(raw_file_path),
            "chunk_index": i
        }
        
        qdrant.upsert(
            collection_name=collection_name,
            vector=vector,
            payload=payload,
            point_id=point_id
        )
        
        # --- GRAPH PIPELINE ---
        print("  -> Extracting graph entities via local LLM...")
        relationships = extract_entities_and_relationships(chunk, llm)
        
        if relationships:
            print(f"  -> Found {len(relationships)} relationships. Loading to Neo4j...")
            for rel in relationships:
                source = rel.get("source")
                target = rel.get("target")
                rel_type_raw = rel.get("relationship", "RELATES_TO")

                if not source or not target:
                    continue

                # Sanitize relationship type for Cypher (must be alphanumeric/underscore)
                rel_type = re.sub(r'[^A-Z0-9_]', '_', str(rel_type_raw).upper())
                
                # Ensure relationship type is not empty after filtering and doesn't start with a number
                if not rel_type or rel_type[0].isdigit():
                    rel_type = f"REL_{rel_type}" if rel_type else "RELATES_TO"

                cypher = f"""
                MERGE (s:Entity {{name: $source}})
                MERGE (t:Entity {{name: $target}})
                MERGE (s)-[:{rel_type}]->(t)
                """
                neo4j.execute_query(cypher, {"source": source, "target": target})

    neo4j.close()
    print("\n✅ ETL Pipeline Complete!")

if __name__ == "__main__":
    main()
    