import json
from backend.interfaces.llm_client import BaseLLMClient

def extract_entities_and_relationships(text_chunk: str, llm_client: BaseLLMClient) -> list[dict]:
    """
    Uses an LLM to extract a knowledge graph structure from a text chunk.

    Args:
        text_chunk (str): The text segment to analyze.
        llm_client (BaseLLMClient): An injected LLM client to perform the extraction.

    Returns:
        list[dict]: A list of dictionaries, where each dict represents a relationship.
            Example: [{"source": "Concept A", "relationship": "RELATES_TO", "target": "Concept B"}]
    """
    prompt = f"""
    You are a highly precise data extraction pipeline. 
    Analyze the following text and extract the key entities and the relationships between them.
    
    Rules:
    1. Output ONLY a valid JSON array of objects.
    2. Each object must have exactly three keys: 'source', 'relationship', 'target'.
    3. Do not include markdown formatting like ```json or any other commentary.
    
    Text to analyze:
    {text_chunk}
    """
    
    # We pass keep_alive="1h" to ensure the model stays in memory during batch processing
    raw_response = llm_client.generate(prompt=prompt, keep_alive="1h")
    
    try:
        # Clean the response in case the LLM ignored rule #3
        clean_response = raw_response.strip().strip('```json').strip('```')
        return json.loads(clean_response)
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM output as JSON. Output was: {raw_response}")
        return []
        