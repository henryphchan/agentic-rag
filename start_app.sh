#!/bin/bash

# 1. Ensure the virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

echo "🚀 Starting Agentic RAG Application..."

# 2. Define a cleanup function to gracefully shut down background processes
cleanup() {
    echo ""
    echo "🛑 Caught termination signal. Shutting down servers..."
    # Kill the FastAPI background process
    kill $BACKEND_PID 2>/dev/null
    wait $BACKEND_PID 2>/dev/null
    echo "✅ Application stopped gracefully. Ports are clean."
    exit
}

# 3. Trap Ctrl+C (SIGINT) and call the cleanup function
trap cleanup SIGINT SIGTERM

# 4. Start the FastAPI backend in the background
echo "  -> Booting up FastAPI Backend (Port 8000)..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
# Save the Process ID of the backend so we can kill it later
BACKEND_PID=$!

# Wait a brief moment for the backend to initialize before starting the UI
sleep 3

# 5. Start the Streamlit frontend in the foreground
echo "  -> Booting up Streamlit Frontend (Port 8501)..."
# We bind to 0.0.0.0 so you can access it via your VM's IP address if needed
streamlit run frontend/app.py --server.address 0.0.0.0

# The script will hold here while Streamlit runs.
# When you press Ctrl+C, the trap triggers the cleanup function.
