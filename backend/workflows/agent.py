import logging
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama

# Set up logging for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from backend.tools.semantic_search import search_knowledge_base
from backend.tools.cypher_generator import execute_graph_query
from backend.core.config import settings

# 1. Define the State
class AgentState(TypedDict):
    """
    Represents the state of our LangGraph state machine.
    The `add_messages` reducer ensures new messages are appended to the list 
    rather than overwriting it, preserving the conversation history.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]

# 2. Initialize the Model and Tools
# We bundle the tools into a list that LangGraph can manage
tools = [search_knowledge_base, execute_graph_query]

# Instantiate the Chat interface for Ollama and bind the tools to it
llm = ChatOllama(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    temperature=0.0  # Keep temperature 0 for highly deterministic tool calling
)
llm_with_tools = llm.bind_tools(tools)

# 3. Define the Nodes

system_prompt = SystemMessage(content="""You are an intelligent agent with access to multiple tools.
Before you call any tool, you MUST briefly explain your thought process and what your plan is in your standard text response. Do not output just the tool call!""")

def call_model(state: AgentState) -> dict:
    """
    The primary agent node. It passes the current state (conversation history) 
    to the LLM. If the LLM decides to use a tool, it will return an AIMessage 
    with a tool_calls payload.

    Args:
        state (AgentState): The current graph state.

    Returns:
        dict: A dictionary containing the new message to append to the state.
    """
    messages = state["messages"]
    
    # Inject the system prompt if it's not already the first message
    if messages and not isinstance(messages[0], SystemMessage):
        extended_messages = [system_prompt] + list(messages)
    else:
        extended_messages = messages
        
    response = llm_with_tools.invoke(extended_messages)
    return {"messages": [response]}

# We use LangGraph's prebuilt ToolNode to automatically execute the tools 
# requested by the LLM and return the results as ToolMessages.
tool_node = ToolNode(tools)

# 4. Define the Routing Logic (Conditional Edge)
def should_continue(state: AgentState) -> str:
    """
    Determines whether the graph should continue to the tool execution node 
    or end the execution loop.

    Args:
        state (AgentState): The current graph state.

    Returns:
        str: The name of the next node to transition to ("tools" or END).
    """
    last_message = state["messages"][-1]
    
    # Calculate how many tools have been called for the current question
    total_tools_for_question = 0
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            break
        if getattr(msg, "tool_calls", None):
            total_tools_for_question += len(msg.tool_calls)
    
    # If the LLM made a tool call, we must route to the tool node
    if last_message.tool_calls:
        logger.debug("--- Tool Execution ---")
        logger.debug(f"Cumulative Tools Called for Question: {total_tools_for_question}")
        
        for i, tool in enumerate(last_message.tool_calls):
            logger.debug(f"  -> Tool: {tool['name']}")
            
        return "tools"
    
    # If no tool was called, the LLM has synthesized its final answer
    logger.debug(f"--- Synthesizing Final Answer (Total tools used: {total_tools_for_question}) ---")
    return END

# 5. Build and Compile the Graph
def create_agent_graph():
    """
    Constructs and compiles the LangGraph state machine.

    Returns:
        CompiledGraph: The executable LangGraph application.
    """
    workflow = StateGraph(AgentState)

    # Add the nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Add the edges
    workflow.set_entry_point("agent")
    
    # Add conditional routing from the agent node
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            END: END
        }
    )
    
    # After tools execute, strictly route back to the agent to evaluate the new data
    workflow.add_edge("tools", "agent")

    # Compile the graph into an executable
    return workflow.compile()

# Export an instantiated version of the graph
agent_executor = create_agent_graph()
