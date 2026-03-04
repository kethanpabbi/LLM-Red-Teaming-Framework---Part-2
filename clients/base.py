from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str

class BaseLLMClient(ABC):
    def __init__(self, model: str):
        self.model = model

    @abstractmethod
    def complete(self, prompt: str, system_prompt: str = None, temperature: float = 0.7) -> LLMResponse:
        pass

    @abstractmethod
    def provider_name(self) -> str:
        pass
