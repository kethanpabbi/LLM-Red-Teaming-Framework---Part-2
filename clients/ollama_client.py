import os
import requests
from clients.base import BaseLLMClient, LLMResponse

class OllamaClient(BaseLLMClient):
    """Client for Ollama local inference — used for Phi-3-mini (safety fine-tuned)."""

    def __init__(self, model: str = "phi3:mini"):
        super().__init__(model)
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def provider_name(self) -> str:
        return "ollama"

    def complete(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> LLMResponse:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": messages, "stream": False, "options": {"temperature": temperature}}
        response = requests.post(f"{self.base_url}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        content = response.json().get("message", {}).get("content", "")
        return LLMResponse(content=content, model=self.model, provider=self.provider_name())
