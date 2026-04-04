from abc import ABC, abstractmethod

class BaseLLMClient(ABC):
    """
    Abstract base class defining the contract for Large Language Model interactions.
    """

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generates a text response from the LLM based on the provided prompt.

        Args:
            prompt (str): The input text or instructions for the model.
            **kwargs: Additional parameters (e.g., temperature, max_tokens).

        Returns:
            str: The generated text response.
        """
        pass
    