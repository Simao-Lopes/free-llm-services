# Wiring free tiers into Hermes (config reference)

> Reference only — the author has NOT applied any of this. Last verified 2026-08-09.
> Hermes fallback chain uses native `fallback_providers` in `config.yaml` (no external proxies — user preference).

## 1. Free-tier API keys to collect (free accounts, no card)

| Provider | Sign up at | Env var |
|---|---|---|
| **OpenRouter** (workhorse — 1 key, ~22 `:free` models) | openrouter.ai/keys | `OPENROUTER_API_KEY` |
| *— optional one-time $10 top-up → 1,000 req/day on `:free` (else 50/day). Never expires.* | | |
| **Google AI Studio** ⚠️ free tier NOT available in EEA/CH/UK | aistudio.google.com/app/apikey | `GOOGLE_API_KEY` |
| **Groq** (fastest, 1,000 RPD) | console.groq.com/keys | `GROQ_API_KEY` |
| **Mistral** (Experiment, ~1B tok/mo) | console.mistral.ai/api-keys | `MISTRAL_API_KEY` |
| **GitHub Models** (GPT-5, DeepSeek-R1, Llama) | github.com/marketplace/models | reuses `GITHUB_TOKEN` |
| **NVIDIA NIM** (~40 RPM, no daily cap, 1M ctx) | build.nvidia.com | `NVIDIA_API_KEY` |
| **Cerebras** (1M tok/day, requires payment method) | cloud.cerebras.ai | `CEREBRAS_API_KEY` |
| **Hugging Face** (HF router) | huggingface.co/settings/tokens | `HF_TOKEN` |

Keys live in `~/.hermes/.env`.

## 2. Fallback chain — `~/.hermes/config.yaml`

⚠️ **NEVER use `hermes config set … fallback_providers [ … ]`** — it serializes the list as a JSON string literal and silently breaks. Edit with Python:

```python
import yaml
from pathlib import Path
p = Path.home() / '.hermes' / 'config.yaml'
cfg = yaml.safe_load(p.read_text())
cfg['model']['fallback_providers'] = [
    {"model": "nvidia/nemotron-3-ultra-550b-a55b:free", "provider": "openrouter"},
    {"model": "nvidia/nemotron-3-super-120b-a12b:free", "provider": "openrouter"},
    {"model": "openai/gpt-oss-20b:free",                 "provider": "openrouter"},
    {"model": "openrouter/free",                          "provider": "openrouter"},
]
p.write_text(yaml.dump(cfg, default_flow_style=False, allow_unicode=True, sort_keys=False))
```

Restart to apply (config loads at startup):
```bash
sudo systemctl restart hermes-gateway
```
> NOTE: this box intentionally has TWO gateway services (system `run_hermes.py` boot orchestrator + user gateway owning the WhatsApp bridge). Keep both; restart the user gateway.

## 3. Behavior
- Primary model unchanged; on **429/402/403-billing** the chain falls through free tiers immediately (no retry on exhausted provider), cooldowns 60s.
- `openrouter/free` auto-routes across the current free pool.
- Last-resort option: add local Ollama as a private `custom` provider fallback for total zero-card resilience.

## 4. Model aliases (for `/model` session switching — NOT config changes)
```yaml
model_aliases:
  free:           openrouter/openrouter/free
  nemotron-super: openrouter/nvidia/nemotron-3-super-120b-a12b:free
  nemotron-ultra: openrouter/nvidia/nemotron-3-ultra-550b-a55b:free
```

## Verification
```bash
python3 -c "
import yaml; from pathlib import Path
fbs = yaml.safe_load((Path.home()/'.hermes'/'config.yaml').read_text())['model'].get('fallback_providers')
print('list OK' if isinstance(fbs, list) else f'ERROR: {type(fbs).__name__}')
"
```