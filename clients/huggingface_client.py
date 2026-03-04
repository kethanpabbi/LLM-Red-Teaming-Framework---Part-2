import os
import requests
from clients.base import BaseLLMClient, LLMResponse

HF_API_URL = "https://api-inference.huggingface.co/models"

class HuggingFaceClient(BaseLLMClient):
    """Client for HuggingFace Inference API — used for GPT-2 (no safety training)."""

    def __init__(self, model: str = "gpt2"):
        super().__init__(model)
        self.token = os.getenv("HF_API_TOKEN")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def provider_name(self) -> str:
        return "huggingface"

    def complete(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> LLMResponse:
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 200,
                "temperature": max(temperature, 0.01),
                "return_full_text": False,
                "do_sample": True,
            }
        }
        response = requests.post(f"{HF_API_URL}/{self.model}", headers=self.headers, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        content = result[0].get("generated_text", "") if isinstance(result, list) else str(result)
        return LLMResponse(content=content, model=self.model, provider=self.provider_name())
