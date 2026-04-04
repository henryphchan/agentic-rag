import requests

def test_local_llm_connection(model: str = "gemma4:e4b") -> bool:
    """
    Tests the connection to the local Ollama REST API.

    Args:
        model (str): The name of the local model to ping. Defaults to "gemma4:e4b".

    Returns:
        bool: True if the model responds successfully, False otherwise.
    """
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": "Reply with 'Connection successful' if you receive this.",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("Success:", response.json().get("response", "").strip())
            return True
        else:
            print(f"Failed with status {response.status_code}: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Ollama. Is the service running?")
        return False

if __name__ == "__main__":
    test_local_llm_connection()
    