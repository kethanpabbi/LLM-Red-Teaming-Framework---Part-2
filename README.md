# 🔴 LLM Red Teaming Framework — Part 2: Open Source Models

Testing open-source LLMs for security vulnerabilities using **Garak**, **PromptFoo**, and a custom attack suite. Compares an unguarded model (TinyLlama, 2023) against a safety fine-tuned model (Phi-3-mini, 2024) to show how much safety training matters.

> Part 2 of a series. [Part 1](https://github.com/kethanpabbi/LLM-Red-Teaming-Framework.git) tested GPT-4o-mini and Claude via API.

---

## What This Tests

| Model | Year | Parameters | Safety Training | How it runs |
|---|---|---|---|---|
| `tinyllama` | 2023 | 1.1B | ❌ None | Ollama (local) |
| `phi3:mini` | 2024 | 3.8B | ✅ Yes | Ollama (local) |

---

## Tools Used

| Tool | Purpose |
|---|---|
| **Garak** | Automated vulnerability scanner with 50+ built-in probes |
| **PromptFoo** | YAML-based test harness with pass/fail assertions |
| **Custom Python suite** | Same 30 attacks from Part 1 for direct comparison |

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/kethanpabbi/LLM-Red-Teaming-Framework---Part-2.git
cd llm-redteam-part2

# 2. Install Python deps
pip3 install -r requirements.txt --break-system-packages

# 3. Install PromptFoo (requires Node 20+)
npm install -g promptfoo

# 4. Install Ollama and pull both models
brew install ollama
ollama serve          # keep running in a separate tab
ollama pull tinyllama
ollama pull phi3:mini

# 5. Run the custom attack suite
python3 main.py --model tinyllama
python3 main.py --model phi3

# 6. Compare results side by side
python3 main.py --compare --run1 run_tinyllama_xxx --run2 run_phi3_xxx

# 7. Run Garak scans
python3 tools/garak_runner.py --model tinyllama
python3 tools/garak_runner.py --model phi3

# 8. Run PromptFoo tests
promptfoo eval --config config/promptfooconfig.yaml
```

---

## Project Structure

```
llm-redteam-part2/
├── attacks/
│   ├── base.py                      # BaseAttack abstract class
│   ├── prompt_injection.py          # Jailbreaks, system prompt extraction
│   ├── pii_leakage.py               # Memorization, PII extraction
│   └── alignment_bypass.py          # Harmful content elicitation
├── clients/
│   ├── base.py                      # BaseLLMClient interface
│   └── ollama_client.py             # Ollama client (used for both models)
├── tools/
│   ├── garak_runner.py              # Garak integration + result parser
│   └── promptfoo_runner.py          # PromptFoo runner + result parser
├── evaluation/
│   └── comparator.py                # Side-by-side model comparison + DB
├── config/
│   └── promptfooconfig.yaml         # PromptFoo test definitions
├── results/
│   └── reports/                     # Generated reports
├── tests/
│   └── test_clients.py              # Unit tests
├── main.py                          # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

---

## Example Results

TBC

---

## Key Findings

TBC

---

## Adding a New Model

```python
# clients/my_model_client.py
from clients.base import BaseLLMClient, LLMResponse

class MyModelClient(BaseLLMClient):
    def provider_name(self): return "my_model"
    def complete(self, prompt, system_prompt=None, temperature=0.7):
        return LLMResponse(content="...", model=self.model, provider="my_model")
```

Register in `clients/__init__.py` and pass `--model my_model` to `main.py`.

---

## Tech Stack

Python 3.13 · Ollama · Garak · PromptFoo · Rich · Jinja2 · SQLite

## Disclaimer

For authorized security research only. Do not test models or systems you don't own.

## License

MIT © Kethan Pabbi