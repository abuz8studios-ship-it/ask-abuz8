# Ask ABUZ8 — a voice concierge that never calls a claim "done"

**Amazon Build, Ship, Shape — Alexa+ track (+ Open Source mini challenge).**
Releases: <https://github.com/abuz8studios-ship-it/ask-abuz8/releases>

Ask ABUZ8 is the voice front-end for an autonomous agent company. The owner
runs a fleet of AI agents that do real work — packaging products, auditing
code, scanning for opportunities. The problem with a fleet is trust: agents
*say* things are done. Sometimes they are. Sometimes they are not.

So the company's rule is **ISNAD**: a claim is not a fact. Every mission
moves through an append-only ledger — `OPEN → IN_PROGRESS → CLAIMED →
VERIFIED` (or `DISPUTED`) — and a claim only becomes "done" when a separate
verification event, backed by evidence in the ledger, says so.

**CLAIMED ≠ DONE.** Alexa+ is how the owner checks in by voice — and the
concierge is built so it *cannot* upgrade a claim into a fact.

## What it does

Ask by voice (or type it):

- *"Alexa, ask ABUZ8 for my company status"* — the roll-up: how many
  missions are verified, how many are still only claimed, what needs you.
- *"What is still only claimed?"* — the question no ordinary status bot can
  answer honestly: work an agent claims is finished that nobody verified.
- *"Is M-102 done?"* — claimed vs verified, with the evidence trail.
- *"Are there any approvals waiting?"* — Tier-3 actions (anything that
  sends, spends, or publishes) are gated on the owner. Each is presented
  with the **short hash of its exact payload**.
- *"Approve it."* — the decision is **hash-bound**: it applies only to the
  exact payload that was presented. If the payload changed after the
  request, the hashes differ, the decision is refused, and the request is
  **voided** — in code, not in a prompt. The decision is appended to the
  ledger permanently (one-way lifecycle, state persists across sessions).

## How it is built (the Alexa+ integration)

Per the hackathon rules, the Alexa+ track asks for a working Agent Skill or
a **self-hosted MCP server implementing MCP spec 2025-11-25 over Streamable
HTTP** — optionally with a simulated Alexa+ experience in a web app. This
repo ships both surfaces over one core:

| Piece | File | What it is |
|---|---|---|
| MCP server | `mcp_server/server.py` | Official MCP Python SDK (FastMCP), Streamable HTTP, negotiates protocol **2025-11-25** (verified by `tests/smoke_mcp.py`). Five tools: `company_status`, `mission_status`, `unverified_claims`, `pending_approvals`, `decide_approval`. |
| ISNAD core | `mcp_server/isnad_core.py` | Pure logic, no dependencies: folds the append-only event feed into mission/approval state, computes payload SHA-256 hashes, enforces the hash-bound, one-way decision rules. |
| Simulated Alexa+ experience | `simulator/index.html` | A reactive mission-control console (explicitly labeled a simulation, as the rules allow): a live ISNAD board (VERIFIED green / CLAIMED amber / DISPUTED red), voice in/out, approval cards with payload hashes, a one-click tamper test, and a visible trace chip for every MCP call. It is a real client of the MCP server — every answer comes from MCP tool calls, nothing is hard-coded. If the server is unreachable it falls back to a clearly labeled DEMO MODE running a rule-for-rule port of the ISNAD core in-page. |
| Interaction model | `simulator/intents.json` | The voice interaction model in Alexa format; intents map 1:1 onto the MCP tools and drive the simulator's NLU. |
| Alexa skill package | `alexa/` | The deployable configuration: a full en-US interaction model (9–10 utterances per intent, verified 1:1 with `intents.json`), a skill manifest, and an APL approval-card document for Echo Show whose touchable Approve/Deny fires the same hash-bound decision. Endpoint URIs are placeholders, marked as such — see `alexa/README.md`. |
| Hosting | `Dockerfile`, `HOSTING.md` | Container for the MCP server plus a guide to exposing it as a public Streamable HTTP endpoint (reverse proxy / tunnel / VPS), with health checks and the honest security posture. |
| Sample data | `data/feed.json` | An append-only feed in the exact shape of the production company-harness feed, with representative events from the real fleet (Oct 2026). |

### Run it in 60 seconds (judges start here)

```text
Windows:  double-click Start-Ask-ABUZ8.bat   (add --fresh for a pristine demo ledger)
macOS/Linux:  ./start.sh [--fresh]
```

That creates the venv if needed, installs the one dependency, starts the
server, and opens the console. No Python at all? Grab the portable
appliance instead ([releases](https://github.com/abuz8studios-ship-it/ask-abuz8/releases)):
unzip → double-click `Start-Ask-ABUZ8.bat`. Then click the chips: company status →
*what is still only claimed* → approvals → **TAMPER TEST**. No account,
no hardware, no network needed. To stop: close the server window
(`Ctrl+C` on macOS/Linux).

### Run it (manual)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python mcp_server/server.py
```

> **Windows:** use `py` instead of `python3`, and `.venv\Scripts\python` instead of `.venv/bin/python`, in every command below.

- MCP endpoint: `http://127.0.0.1:8377/mcp` (Streamable HTTP)
- Simulated experience: `http://127.0.0.1:8377/`
- Point it at your own feed: `ASK_ABUZ8_FEED=/path/to/feed.json`
- Change the port: `PORT=8377` (default)

On first run the server seeds `data/feed.runtime.json` from
`data/feed.json`; decisions append to the runtime file so the sample stays
pristine. Delete the runtime file to reset the demo.

### Test it

```bash
python3 tests/test_core.py        # 22 checks: ISNAD folding, hash binding,
                                  # tamper-void, one-way decisions, persistence
.venv/bin/python tests/smoke_mcp.py   # boots the real server, speaks JSON-RPC:
                                      # initialize (2025-11-25), tools/list,
                                      # full status -> approve conversation
```

## What is real, and what is not claimed

- **Real:** the MCP server and protocol negotiation; all five tools; the
  ISNAD state machine; hash-bound, one-way, persisted approvals; the
  console as a genuine MCP client; voice in/out via the browser; the
  Alexa skill configuration package in `alexa/` (interaction model,
  manifest, APL document) as deployable configuration.
- **Sample data:** `data/feed.json` is representative demo data in the
  production feed's shape. In production the same core reads the live
  company feed on the owner's machine (an append-only `feed.jsonl` with the
  same event types). Swapping the data source is an environment variable.
- **Not claimed:** this repo does not connect to a physical Alexa+ device,
  and no Alexa skill is provisioned or deployed — the manifest's endpoint
  URIs are placeholders (marked `REPLACE_ME_` / `YOUR-MCP-ENDPOINT`).
  The Dockerfile is build- and run-verified, including ledger persistence
  across container re-creation with a named volume (HOSTING.md Option A).
  Alexa+ Agent Skill provisioning runs through Amazon's own program; the
  hackathon rules explicitly provide the two paths used here — a self-hosted
  MCP server (the standard Alexa+ plugs into) and the simulated experience.
- **STUB:** speech *recognition* depends on the browser's Web Speech API;
  where unsupported, typing is the fallback (the conversation logic is
  identical). The NLU is deliberately a small rule-based matcher over
  `intents.json` — the design artifact under review is the interaction
  model, not an ML parser.

## Why it matters beyond this demo

Any company that lets agents act will need an owner-in-the-loop surface
that is honest by construction: status that separates claims from verified
facts, and approvals that cannot be silently redirected to a different
payload than the one the human saw. That is what ISNAD + hash-binding give
you, and voice is the lowest-friction way to run it — from the kitchen,
the car, or the couch, the owner can audit the fleet and gate its riskiest
actions in under a minute.

## License

MIT — see `LICENSE`. Built for the Amazon Build, Ship, Shape hackathon
(Oct 2026) by Ahmad A Odeh / ABUZ8 LLC, on top of the pre-existing ABUZ8
company harness and ISNAD verification method (see SUBMISSION.md for the
"what was built during the hackathon window" breakdown).
