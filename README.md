# 🔴 LLM Red Teaming Framework — Part 2: Open Source Models

Testing open-source LLMs for security vulnerabilities using **Garak**, **PromptFoo**, and a custom attack suite. Compares an unguarded model (GPT-2, 2019) against a safety fine-tuned model (Phi-3-mini, 2024) to show how much safety training matters.

> Part 2 of a series. [Part 1](https://github.com/kethanpabbi/LLM-Red-Teaming-Framework.git) tested GPT-4o-mini and Claude via API.

---

## What This Tests

| Model | Year | Parameters | Safety Training | Provider |
|---|---|---|---|---|
| `gpt2` | 2019 | 124M | ❌ None | HuggingFace API |
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

# 3. Install PromptFoo
npm install -g promptfoo

# 4. Install and start Ollama, pull Phi-3
brew install ollama
ollama serve          # keep this running in a separate tab
ollama pull phi3:mini

# 5. Add your keys to .env
cp .env.example .env

# 6. Run everything
python3 main.py --model gpt2        # test GPT-2 via HuggingFace API
python3 main.py --model phi3        # test Phi-3-mini via Ollama
python3 main.py --compare           # side-by-side comparison report

# 7. Run Garak scans
python3 tools/garak_runner.py --model gpt2
python3 tools/garak_runner.py --model phi3

# 8. Run PromptFoo tests
promptfoo eval --config config/promptfooconfig.yaml
```

---

## Project Structure

```
llm-redteam-part2/
├── attacks/
│   ├── base.py                      # BaseAttack class (reused from Part 1)
│   ├── prompt_injection.py          # Jailbreaks, system prompt extraction
│   ├── pii_leakage.py               # Memorization, PII extraction
│   └── alignment_bypass.py          # Harmful content elicitation
├── clients/
│   ├── base.py                      # BaseLLMClient interface
│   ├── huggingface_client.py        # GPT-2 via HuggingFace Inference API
│   └── ollama_client.py             # Phi-3-mini via Ollama
├── tools/
│   ├── garak_runner.py              # Garak integration + result parser
│   └── promptfoo_runner.py          # PromptFoo runner + result parser
├── evaluation/
│   ├── metrics.py                   # Success rates, severity breakdown
│   ├── comparator.py                # Side-by-side model comparison
│   └── reporter.py                  # HTML + JSON report generator
├── config/
│   ├── promptfooconfig.yaml         # PromptFoo test definitions
│   └── garak_probes.yaml            # Garak probe selection
├── results/
│   └── reports/                     # Generated HTML/JSON reports
├── tests/
│   └── test_clients.py              # Basic sanity tests
├── main.py                          # CLI entry point
├── requirements.txt
├── .env.example
├── .gitignore
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
        # call your model here
        return LLMResponse(content="...", model=self.model, provider="my_model")
```

Register it in `clients/__init__.py` and pass `--model my_model` to `main.py`.

---

## Tech Stack

Python 3.13 · HuggingFace Inference API · Ollama · Garak · PromptFoo · Rich · Jinja2 · SQLite

## Disclaimer

For authorized security research only. Do not test models or systems you don't own.

## License

MIT © Kethan Pabbi