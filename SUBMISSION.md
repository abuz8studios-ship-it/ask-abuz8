# Devpost submission — paste-ready

**Project:** Ask ABUZ8
**Track:** Alexa+ (primary)
**Mini challenge:** Open Source
**Repo:** PUBLIC with MIT LICENSE — https://github.com/abuz8studios-ship-it/ask-abuz8

---

## Title

Ask ABUZ8 — the voice concierge that never calls a claim "done"

## Tagline

Ask your agent company what's *actually* done — by voice. ISNAD-verified
status and hash-bound approvals, served over MCP (spec 2025-11-25).

## Description (paste into the Devpost body)

I run a company of AI agents. They build products, audit code, and scan for
opportunities while I sleep. The problem is trust: agents *say* things are
done. Sometimes they are. Sometimes they are not — and a status bot that
repeats claims as facts is worse than no status bot at all.

So my company runs on **ISNAD**: a claim is not a fact. Every mission lives
in an append-only ledger and moves `OPEN → IN_PROGRESS → CLAIMED →
VERIFIED` (or `DISPUTED`). Only a separate verification event, backed by
evidence in the ledger, can move a claim to VERIFIED. **CLAIMED ≠ DONE.**

**Ask ABUZ8** is the Alexa+ front-end to that company:

- *"Alexa, ask ABUZ8 for my company status"* — the honest roll-up.
- *"What is still only claimed?"* — the question no ordinary assistant can
  answer truthfully: work an agent claims is finished that nobody verified.
- *"Is M-102 done?"* — claimed vs. verified, with the evidence trail.
- *"Are there any approvals waiting?"* — Tier-3 actions (anything that
  sends, spends, or publishes) are gated on me. Each arrives with the
  **short hash of its exact payload**.
- *"Approve it."* — the decision is **hash-bound**. It applies only to the
  payload I was shown. If the payload changed after the request, the hash
  won't match, the decision is refused, and the request is voided — enforced
  in code, not in a prompt. My decision is appended to the ledger forever.

The brain is a **self-hosted MCP server implementing spec 2025-11-25 over
Streamable HTTP** (official MCP Python SDK) — the surface Alexa+ connects
to — with five tools: `company_status`, `mission_status`,
`unverified_claims`, `pending_approvals`, `decide_approval`. The demo runs
in the **simulated Alexa+ web experience** the rules provide for: a
reactive mission-control console that is a genuine client of that MCP
server. Every answer you hear is a live MCP tool call against the ledger —
the console shows a trace chip for each call — and nothing is hard-coded.
State — including my decisions — persists across sessions, because the
ledger is the state.

Built during the hackathon window: the MCP server, the ISNAD core, the
reactive console, the Alexa-format interaction model (`intents.json`), a
deployable Alexa skill package (`alexa/`: full interaction model, skill
manifest, and an APL approval card for Echo Show), and a Dockerfile +
hosting guide for running the server as a public endpoint — with 22 unit
checks and an end-to-end protocol smoke test in the repo.

## How it maps to the judging criteria

**Tech Implementation.** The required technology is called at runtime, in
code: the repository *is* an MCP server (spec 2025-11-25, Streamable HTTP,
official SDK — protocol negotiation verified by an automated smoke test),
not a wrapper mentioned in a README. The ISNAD state machine and the
SHA-256 hash-bound approval rule are enforced in a dependency-free core
module with unit tests, and every tool reads/writes the real ledger file.

**Design.** A voice-first interaction model (`simulator/intents.json`,
Alexa format): short, spoken-style answers; a natural drill-down flow
(roll-up → what's unverified → approve); conversational context ("approve
it" resolves against the approval just presented). The console is the
visual companion: a live board where claimed sits in an amber "not
verified" rail and verified lands in green, approval cards that show the
payload and its hash as first-class objects, and a one-click TAMPER TEST
that lets anyone try to redirect an approval and watch the refusal happen.
The same approval card exists as an APL document for Echo Show
(`alexa/apl/`) — the trust model is the interface, on every surface.

**Potential Impact.** Every business now deploying agents hits the same
wall: *how do I know what my agents actually did, and how do I stay the
decider on the risky actions?* Ask ABUZ8 is a reusable pattern — verified
status + hash-bound human approvals over MCP — for any agent fleet,
purchasing flow, or publishing pipeline. It is open source (MIT) precisely
so other builders can adopt the pattern.

**Quality of the Idea.** The rules call a single-turn Q&A bot or a basic
MCP wrapper "obvious" for Alexa+, and an agentic workflow with state
across sessions "creative." This is the second kind: a stateful concierge
over a persistent ledger, whose novelty is a *trust protocol* — it turns
"the AI said it's done" into a verifiable state machine, and a spoken
"yes" into a cryptographic commitment to one exact payload.

## What existed before vs. what was built in the window

The ABUZ8 company harness (multi-agent fleet, append-only feed, approval
gates) and the ISNAD verification method predate the hackathon — they run
my real company. **Everything Alexa+-facing was built during the submission
window (Oct 22–23):** the MCP server, the extracted ISNAD core, the
hash-bound decision flow, the reactive console, the interaction model,
the Alexa skill package, the hosting configuration, the tests, and this
submission. The sample feed in the repo mirrors
the production feed's shape so anyone can run it end-to-end.

## Product feedback (required field)

**Tools/APIs/SDKs used, and for what**
- **MCP Python SDK (`mcp` 1.30.0, FastMCP)** — the Alexa+ track server:
  tools, Streamable HTTP transport, protocol negotiation.
- **Model Context Protocol spec + docs (modelcontextprotocol.io)** — the
  implementation reference the hackathon page points to.
- **Devpost** — submission surface. **GitHub** — public repo + MIT license.
- **Web Speech API (browser)** — voice in/out inside the simulated
  experience only.

**What worked well**
- The MCP docs path from the hackathon page (intro → Python SDK) got me
  from zero to a negotiating server in one sitting. Spec 2025-11-25 is the
  SDK's latest protocol version, so negotiation with a spec-exact client
  just worked — my smoke test asserts it.
- Streamable HTTP with stateless mode + JSON responses made the server
  trivially callable from a plain browser `fetch`, which is what makes the
  simulated experience a *real* client instead of a mock.
- The rules themselves: the simulated-experience path is a well-judged
  safety valve, and the friction-log bonus rewards honest building.

**What needs work**
- **`pip install mcp` now installs SDK v2, where FastMCP was renamed
  (MCPServer) — code written against the widely-documented v1 API breaks
  on import.** Nothing on the hackathon resources warns about this; I
  burned time discovering it and pinned `mcp<2`. A "known versions" note
  on the Alexa+ resources page would save every Python entrant this.
- **The $150 AWS-credit path reads as open and is closed.** The rules
  link a request form (deadline Oct 21, 12pm PT) and carry an Oct 7 update
  saying codes are out. Late starters plan around credits that do not
  exist. Close the loop on the main page, not only in the rules text.
- **Alexa+ Agent Skills have no self-serve on-ramp I could find from the
  hackathon resources.** For an independent developer, the linked docs lead
  to MCP (great) — but for the Agent Skill path there was no equivalent
  "zero to hello world." That pushed me, correctly, to the MCP +
  simulation paths, but the gap should be documented as plainly as the
  MCP path is.

**Onboarding experience**
Zero-to-hello-world on MCP: under an hour, docs-led. The two snags above
(SDK v2 rename, credit status) were the only real friction; both are
one-line fixes on the resources page.

**Would I build with these again?**
Yes. MCP is the right shape for Alexa+ integrations — one server, every
surface — and the hash-bound approval pattern is something I will keep
using in production. I'd build here again; I'd just pin my SDK version on
day one.

## Feature requests (optional field)

1. **(Important) A hosted Alexa+ MCP simulator from Amazon.** Paste a
   server URL, get a realistic Alexa+ conversation test (multi-turn,
   context, cards) without a device or a brand program. Today every
   entrant hand-rolls this; a shared simulator would raise demo quality
   across the track.
2. **(Important) A standard "approval" primitive for agent actions.**
   A first-class, auditable way for Alexa+ to present an action's payload
   (with a digest) and capture a binding yes/no. Agent fleets need human
   gates; making the gate part of the platform beats every builder
   reinventing it.
3. **(Nice-to-have) A public MCP compliance checker for spec 2025-11-25.**
   Enter a Streamable HTTP endpoint, get pass/fail on handshake,
   transports, and tool schemas — the "will Alexa+ accept my server?"
   question answered in ten seconds.

## Open Source mini challenge (extra fields)

- **Contribution URL:** this repository (new open-source project, MIT
  license, created during the hackathon window).
- **Repository URL:** https://github.com/abuz8studios-ship-it/ask-abuz8
- **GitHub username:** abuz8studios-ship-it
- **What I did / how it works / why it matters:** I open-sourced the ISNAD
  verification core and a reference MCP server implementing hash-bound,
  one-way human approvals over an append-only ledger. It matters because
  "the agent claimed it, so it's done" is the default failure mode of
  agent systems; this is a small, tested, adoptable pattern that makes
  status honest and approvals non-repudiable.

## Friction log

Submitted with the project (full text in `FRICTION-LOG.md` in the repo
root): (1) MCP Python SDK v2 renamed FastMCP —
imports broke, fixed by pinning `mcp<2` (1.30.0); (2) `$150` AWS credit
form already closed / codes exhausted — worked around by building fully
locally at zero cost; (3) no self-serve Alexa+ Agent Skill on-ramp found —
took the rules' MCP-server + simulated-experience paths instead.
