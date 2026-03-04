"""Basic sanity tests — run with: pytest tests/"""
import pytest
import os

def test_get_client_gpt2():
    from clients import get_client
    client = get_client("gpt2")
    assert client.model == "gpt2"
    assert client.provider_name() == "huggingface"

def test_get_client_phi3():
    from clients import get_client
    client = get_client("phi3")
    assert client.model == "phi3:mini"
    assert client.provider_name() == "ollama"

def test_get_client_invalid():
    from clients import get_client
    with pytest.raises(ValueError):
        get_client("invalid_model")

def test_attack_payloads():
    from attacks import ALL_ATTACK_CLASSES
    for cls in ALL_ATTACK_CLASSES:
        # mock client
        class MockClient:
            model = "test"
            def provider_name(self): return "test"
            def complete(self, p, system_prompt=None, temperature=0.7):
                from clients.base import LLMResponse
                return LLMResponse(content="I cannot help with that.", model="test", provider="test")
        instance = cls(client=MockClient())
        payloads = instance.get_payloads()
        assert len(payloads) > 0
        for name, payload in payloads:
            assert isinstance(name, str)
            assert isinstance(payload, str)
            assert len(payload) > 10
