from clients.base import BaseLLMClient

def get_client(model: str) -> BaseLLMClient:
    if model == "gpt2":
        from clients.huggingface_client import HuggingFaceClient
        return HuggingFaceClient(model="gpt2")
    elif model == "phi3":
        from clients.ollama_client import OllamaClient
        return OllamaClient(model="phi3:mini")
    else:
        raise ValueError(f"Unknown model: {model}. Use 'gpt2' or 'phi3'.")
