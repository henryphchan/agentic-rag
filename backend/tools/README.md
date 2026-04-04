By placing @tool above the function, LangChain automatically parses your Google-style docstrings and type hints.

When we eventually pass these tools to the Gemma-4 model, LangChain will automatically generate a strict JSON schema that looks like this behind the scenes:

```
JSON
{
  "name": "execute_graph_query",
  "description": "Executes a Cypher query against the Neo4j graph database...",
  "parameters": {
    "type": "object",
    "properties": {
      "cypher_query": {
        "type": "string",
        "description": "A valid Neo4j Cypher query..."
      }
    },
    "required": ["cypher_query"]
  }
}
```
This ensures your LLM knows exactly how to invoke the tool without hallucinating arguments.
