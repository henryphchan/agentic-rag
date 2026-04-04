import streamlit as st
import requests
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.core.config import settings

# Define the API endpoint.
# Locally, it defaults to your uvicorn server.
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
CHAT_ENDPOINT = f"{API_BASE_URL}/chat"

st.set_page_config(page_title="Agentic RAG Chatbot", page_icon="🤖")

st.title("🤖 Agentic RAG Chatbot")
st.markdown(
    f"**Powered by:** `{settings.LLM_MODEL}` (Reasoning Engine) & "
    f"`{settings.EMBEDDING_MODEL}` (Semantic Search)"
)
st.markdown("Ask questions about your documents. The agent will autonomously query the Graph and Vector databases to find your answer.")

# Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask a question..."):
    
    # 1. Add user message to chat history and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Display an assistant thinking indicator
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("*(Agent is thinking and querying databases...)*")
        
        try:
            # 3. Send the request to your FastAPI backend

            # Extract history (excluding the very last item, which is the current prompt we just appended)
            history_payload = [
                {"role": msg["role"], "content": msg["content"]} 
                for msg in st.session_state.messages[:-1]
            ]

            payload = {"prompt": prompt, "history": history_payload}
            response = requests.post(CHAT_ENDPOINT, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer provided by the API.")
                reasoning_time = data.get("reasoning_time_seconds", 0.0)
                
                # 4. Display the final answer and save to history
                display_text = f"{answer}\n\n*⏱️ Reasoning time: {reasoning_time} seconds*"
                message_placeholder.markdown(display_text)
                st.session_state.messages.append({"role": "assistant", "content": display_text})
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                message_placeholder.markdown(f"**Error:** {error_msg}")
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to the backend API. Is the server running?"
            message_placeholder.markdown(f"**Error:** {error_msg}")
            st.session_state.messages.append({"role": "assistant", "content": error_msg})
            