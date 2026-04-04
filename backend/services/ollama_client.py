import requests
from backend.interfaces.llm_client import BaseLLMClient
from backend.core.config import settings

class OllamaClient(BaseLLMClient):
    """
    Concrete implementation of BaseLLMClient using a local Ollama REST API.
    """

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.LLM_MODEL

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Sends a prompt to the local Ollama instance and returns the generated text.

        Args:
            prompt (str): The input text or instructions.
            **kwargs: Additional parameters. Supports 'keep_alive' to prevent cold starts.

        Returns:
            str: The generated text.
        
        Raises:
            RuntimeError: If the Ollama API returns a non-200 status code.
        """
        url = f"{self.base_url}/api/generate"
        
        # Default to keeping the model loaded for 1 hour for snappy responses
        keep_alive = kwargs.get("keep_alive", "1h")
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": keep_alive
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            return response.json().get("response", "")
        else:
            raise RuntimeError(f"Ollama API Error: {response.status_code} - {response.text}")
            