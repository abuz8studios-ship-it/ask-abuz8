# Ask ABUZ8 on Nebius

Ask ABUZ8 — the front door of a one-person AI company run by autonomous agents — wired to **Nebius Token Factory** and answering live through **NVIDIA Nemotron-3-Nano-30B-A3B**.

Ask's rule is **ISNAD**: a claim is not a fact. Agent work moves `OPEN → IN_PROGRESS → CLAIMED → VERIFIED`, and only a separate verification event can call it done. Money-out, publishing, and irreversible actions always wait for the owner's approval.

## Run it

```bash
export NEBIUS_API_KEY=<your Token Factory key>   # never commit this
python3 app.py                                    # serves on :8899 (PORT env to change)
```

Open http://127.0.0.1:8899/ and ask. Health check: `GET /health`.

No dependencies — Python 3 standard library only.

## How it works

- `POST /api/chat` → Nebius Token Factory `POST /v1/chat/completions`, OpenAI-compatible.
- Base URL: `https://api.tokenfactory.nebius.com/v1/`
- Model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` (262K context; id verified live against `/v1/models` on 2026-10-30).
- System prompt carries the ISNAD doctrine, so answers separate CLAIMED from VERIFIED.

## What Token Factory accelerated

Token Factory gave us an OpenAI-compatible endpoint for an NVIDIA open-weight reasoning model with zero infrastructure work: key → `/v1/models` discovery → live chat completions in minutes. The one integration lesson: Nemotron-3-Nano is a reasoning model, so `max_tokens` must be generous (we use 900) — small budgets return empty `content` because reasoning consumes them. Model ids are case-sensitive; the org prefix is lowercase `nvidia/`.

## Prior work

Ask ABUZ8 predates this hackathon (October 2026: an MCP voice concierge over the ISNAD ledger, with a simulated console and Alexa skill package). **The Nebius Token Factory wiring in this repo — the app answering through Nemotron — is the in-window update built for this hackathon.**

## License

MIT — see the LICENSE file at the root of this repository.
