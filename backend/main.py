from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import time

# Import the compiled LangGraph agent
from backend.workflows.agent import agent_executor

# Initialize the FastAPI app
app = FastAPI(
    title="Agentic RAG API",
    description="Backend API for the Graph/Vector LLM Agent",
    version="1.0.0"
)

# Define the Pydantic schema for the incoming request (Data Validation)
class MessageDict(BaseModel):
    """Represents a single message in the chat history."""
    role: str
    content: str

class ChatRequest(BaseModel):
    """
    The incoming request schema. 
    Expects the current prompt and an optional list of previous messages.
    """
    prompt: str
    history: List[MessageDict] = []

# Define the response schema
class ChatResponse(BaseModel):
    answer: str
    reasoning_time_seconds: float = 0.0

# Define the initial system prompt to set the agent's persona
SYSTEM_PROMPT = SystemMessage(content="""
You are an intelligent corporate intelligence researcher. 
You have access to a vector database for unstructured text and a Neo4j graph database for entity relationships.
Always try to use your tools to find the answer. Answer clearly and concisely.
""")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Accepts a user prompt and conversation history, executes the LangGraph agent, 
    and returns the synthesized answer.
    """
    try:
        # Start building the LangGraph state with the System Persona
        messages = [SYSTEM_PROMPT]
        
        # Append the historical context
        for msg in request.history:
            if msg.role == "user":
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == "assistant":
                messages.append(AIMessage(content=msg.content))
                
        # Append the current question
        messages.append(HumanMessage(content=request.prompt))
        
        initial_state = {"messages": messages}
        
        # Execute the graph
        start_time = time.perf_counter()
        final_state = agent_executor.invoke(initial_state)
        end_time = time.perf_counter()
        reasoning_time = round(end_time - start_time, 2)
        final_ai_message = final_state["messages"][-1].content
        
        return ChatResponse(answer=final_ai_message, reasoning_time_seconds=reasoning_time)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}
    