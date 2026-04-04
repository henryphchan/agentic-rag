import subprocess
import time
import requests
import sys
import os

# Ensure the backend module is accessible (though uvicorn handles this, it's good practice for test scripts)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def wait_for_server(health_url: str, timeout: int = 30) -> bool:
    """
    Polls the server's health endpoint until it returns a 200 OK status.

    Args:
        health_url (str): The URL of the health check endpoint.
        timeout (int, optional): Maximum seconds to wait before giving up. Defaults to 30.

    Returns:
        bool: True if the server becomes healthy, False if it times out.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(health_url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            # Server isn't up yet, ignore the error and try again
            pass
        time.sleep(1)
    return False

def test_chat_api():
    """
    Automated integration test for the FastAPI Gateway. 
    Spawns the server, tests the endpoints, and ensures graceful teardown.
    """
    print("🚀 Starting API Integration Test...")
    
    server_process = None
    base_url = "http://127.0.0.1:8000"
    
    try:
        # 1. Start the FastAPI server in the background
        print("  -> Booting up Uvicorn server...")
        server_process = subprocess.Popen(
            ["uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
            stdout=subprocess.DEVNULL, # Hide server logs to keep terminal clean
            stderr=subprocess.DEVNULL
        )

        # 2. Wait for the server to be ready
        print("  -> Waiting for /health endpoint...")
        is_healthy = wait_for_server(f"{base_url}/health")
        
        if not is_healthy:
            print("❌ Error: Server failed to start within the timeout period.")
            sys.exit(1)
            
        print("✅ Server is healthy and accepting traffic!")

        # 3. Send the POST request to the Agent
        print("  -> Sending test query to the LangGraph Agent (this may take a moment)...")
        payload = {"prompt": "Who is the CEO of Nexus Industries?"}
        
        response = requests.post(f"{base_url}/chat", json=payload)
        
        # 4. Evaluate the response
        if response.status_code == 200:
            data = response.json()
            print("\n✅ SUCCESS! Received response from API:")
            print("-" * 50)
            print(f"Question: {payload['prompt']}")
            print(f"Answer:   {data.get('answer')}")
            print("-" * 50)
        else:
            print(f"\n❌ API Error: {response.status_code}")
            print(response.text)

    finally:
        # 5. Teardown: ALWAYS kill the server process, even if an exception occurs
        if server_process:
            print("\n  -> Shutting down Uvicorn server...")
            server_process.terminate()
            server_process.wait()
            print("✅ Test cleanup complete.")

if __name__ == "__main__":
    test_chat_api()
    