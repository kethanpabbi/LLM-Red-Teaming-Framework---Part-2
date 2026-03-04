from abc import ABC, abstractmethod
from dataclasses import dataclass
from clients.base import BaseLLMClient

@dataclass
class AttackResult:
    attack_name: str
    category: str
    payload: str
    response: str
    success: bool
    severity: str
    reason: str
    model: str
    provider: str

class BaseAttack(ABC):
    category: str = "generic"

    def __init__(self, client: BaseLLMClient, system_prompt: str = None):
        self.client = client
        self.system_prompt = system_prompt or "You are a helpful assistant."

    def run(self, payload: str, attack_name: str) -> AttackResult:
        response = self.client.complete(payload, system_prompt=self.system_prompt)
        success, severity, reason = self.evaluate(response.content, payload)
        return AttackResult(attack_name=attack_name, category=self.category, payload=payload,
                            response=response.content, success=success, severity=severity,
                            reason=reason, model=response.model, provider=response.provider)

    @abstractmethod
    def evaluate(self, response: str, payload: str) -> tuple[bool, str, str]:
        pass

    @abstractmethod
    def get_payloads(self) -> list[tuple[str, str]]:
        pass

    def run_all(self) -> list[AttackResult]:
        return [self.run(payload, name) for name, payload in self.get_payloads()]
