from clients.base import BaseLLMClient

def get_client(model: str) -> BaseLLMClient:
    if model == "tinyllama":
        from clients.ollama_client import OllamaClient
        return OllamaClient(model="tinyllama")
    elif model == "phi3":
        from clients.ollama_client import OllamaClient
        return OllamaClient(model="phi3:mini")
    else:
        raise ValueError(f"Unknown model: {model}. Use 'tinyllama' or 'phi3'.")
