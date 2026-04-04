import sys
import os
from langchain_core.messages import HumanMessage, SystemMessage

# Ensure the backend module is accessible
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.workflows.agent import agent_executor

def test_agent_reasoning():
    """
    Tests the LangGraph agent's ability to autonomously route a user query 
    to the correct database tools and synthesize an answer.
    """
    print("🤖 Waking up Gemma 4 Agent...\n")

    # The System Message gives the agent its persona and initial instructions
    system_prompt = SystemMessage(content="""
    You are an intelligent corporate intelligence researcher. 
    You have access to a vector database for unstructured text and a Neo4j graph database for entity relationships.
    Always try to use your tools to find the answer. Answer clearly and concisely.
    """)

    # A tricky question that requires database lookup
    user_prompt = HumanMessage(content="Who is the Chief Scientist of the company that acquired QuantumCorp?")

    # Initialize the state
    initial_state = {"messages": [system_prompt, user_prompt]}

    print(f"User: {user_prompt.content}")
    print("-" * 50)
    
    # Stream the graph execution to watch its thought process
    for event in agent_executor.stream(initial_state, stream_mode="values"):
        last_message = event["messages"][-1]
        
        # Print what the agent is doing
        if last_message.type == "ai" and last_message.tool_calls:
            print(f"🛠️  Agent decided to use tool: {last_message.tool_calls[0]['name']}")
            print(f"   Arguments: {last_message.tool_calls[0]['args']}")
        elif last_message.type == "tool":
            print(f"📊 Tool returned data: {last_message.content[:100]}...") # truncate for readability
        elif last_message.type == "ai" and not last_message.tool_calls:
            print(f"\n✅ Final Answer:\n{last_message.content}")

if __name__ == "__main__":
    test_agent_reasoning()
    