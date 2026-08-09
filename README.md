# Free LLM Services — perpetual free tiers

Curated list of LLM providers offering **genuinely free, permanent, pay-nothing API access** (raw text inference) — no credit card, no expiry, no trial-countdown for the tier itself.

> **Policy:** this list only includes tiers that are *permanent and free by design*. One-time trial credits (Fireworks $1, Baseten $30, xAI Grok signup credits, DeepSeek trial, & co.) are **excluded** because they run out and may require a card afterward.

## ⚡ Quick picks (best free forever)

- **OpenRouter** — 1 key, ~22 `:free` models, routes + failover. 20 RPM / 50 RPD (1,000 RPD after a one-time $10 top-up).
- **Google AI Studio (Gemini)** — Gemini Flash, up to **1M token context**, 1,500 RPD. *Not available in EU/UK/CH.*
- **Groq** — fastest (Llama 3.3 70B @ ~320 tok/s). 30 RPM / 1,000 RPD.
- **Cerebras** — 1M tokens/day. *Payment method required.*
- **GitHub Models** — GPT-5/4.1, Llama, DeepSeek-R1, Mistral. Tied to your GitHub account.
- **Mistral AI (Experiment)** — ~1B tokens/month, includes Codestral.
- **Ollama Cloud** — 400+ models, measured by GPU time (not tokens).

## 📋 Full list

See **[providers.json](providers.json)** for the machine-readable source of truth (all providers, models, rate limits, notes).

See **[/reports](reports/)** for the dated weekly verification reports.

## 🔍 How verification works

`check.py` runs weekly (via Hermes cron) and, **without touching real API keys**, verifies each provider honestly:

- Reachability of the provider's endpoint/site over HTTP (a 200/401/403/307 all prove the host is alive).
- Best-effort scan of the site/page for a "free tier" indicator.

Status meanings:

| Status | Meaning |
|--------|---------|
| `ok` | reachable + free-tier mention found on scanned page |
| `needs_review` | reachable, but free tier couldn't be confirmed from the homepage (often a JS-rendered console) |
| `unreachable` | host/endpoint did not respond |

> Verification is a reachability + availability check, not a functional API test (no keys are stored here). Treat `needs_review` as "still up; confirm the exact current limits on the provider's pricing page."

## 🧭 Categories

- **provider-api** — run by the company that trains the model (Gemini, Groq, Mistral, Cerebras, Cohere, NIM, Zhipu, SambaNova, SiliconFlow, ModelScope, Aion, Ollama).
- **gateway** — one key + many models / aggregation (OpenRouter, GitHub Models, HF router, OVH, LLM7, Kilo Code).
- **edge** — Cloudflare Workers AI.

## Run the check manually

```bash
python3 check.py
```

## ⚠️ Notes

- Free tiers often log prompts for training — check each provider's policy for sensitive data.
- Limits are reduced/renamed frequently (e.g. Groq dropped from 14,400 → 1,000 RPD in 2026). This repo re-verifies weekly; always confirm current limits on the provider's page before relying on them.
- Regional restrictions apply (Gemini free tier unavailable in EU/UK/CH).

---

*Maintained by Simão Lopes. Auto-checked weekly. Last verified: see `providers.json` → `last_verified`.*