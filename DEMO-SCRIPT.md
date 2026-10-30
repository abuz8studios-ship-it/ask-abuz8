# Demo script — Ask ABUZ8 (target 2:30, hard limit 3:00)

One take, screen recording of the console + your voice. The page speaks
its answers through the browser, so let each answer finish before you go
on. Total spoken words ≈ 360 — comfortable at a natural pace. Everything
stays on the console screen — no terminal shots; the TAMPER TEST is the
climax, not an afterthought.

## Before you press record (2 minutes)

1. Terminal in the project folder:
   `rm -f data/feed.runtime.json` (Windows: `del data\feed.runtime.json`) then
   `.venv/bin/python mcp_server/server.py` (Windows: `.venv\Scripts\python mcp_server/server.py`)
   (fresh ledger: both approvals pending, nothing decided yet)
2. Browser: open `http://127.0.0.1:8377/` — check the LIVE pill is on,
   the board shows M-101 VERIFIED (green), M-102 sitting in the amber
   "Claimed — not verified" rail, and 2 approvals waiting.
3. Mute notifications. You will click the suggestion chips and the
   buttons on the approval cards — they drive the exact beats below.

## The take

**[0:00 — you, over the live board]**
> "I run a company of AI agents. They do real work while I sleep. There's
> one problem: agents *say* things are done — and sometimes they're not.
> So in my company, a claim is not a fact. This is Ask ABUZ8 — Alexa+ as
> the voice concierge to my fleet — and it is built so it cannot call a
> claim 'done'. Green is verified. Amber is only claimed. Watch the
> amber one."

**[0:25 — click chip: "What is still only claimed?"]**
*(the answer streams in and is spoken: M-102, claimed done, NOT verified;
a trace chip shows the live `unverified_claims` call)*
> You: "There. My agent claimed the identity rollout was finished. The
> evidence says the pack was built — but it was never applied, and
> nobody verified it. A normal assistant would have told me 'done'.
> This one can't. The ledger won't let it."

**[0:50 — click chip: "Are there any approvals waiting?"]**
*(the Tier-3 deck renders A-201 as a card: payload table + big hash
`584a201f…`)*
> You: "Anything that sends, spends, or publishes stops here — with me.
> This one wants to publish a $49 product listing. And this hash is the
> fingerprint of the *exact* action I'm being shown. My yes applies to
> this payload — and nothing else."

**[1:15 — click the TAMPER TEST button on A-201]**
*(the console narrates the one-digit edit — price 49 → 499 — submits the
edited payload's hash, and the server answers with the full red banner:
⛔ SERVER REFUSED — APPROVAL VOIDED)*
> You: "Someone changed one digit after I was shown the price. My
> approval was refused — and the request is voided, permanently. Not by
> a prompt asking the AI to behave. By a hash check, in code."

**[1:45 — on A-202, click Approve (or say "Approve it")]**
*(green banner: RECORDED IN THE LEDGER, with the entry number; refresh
the page — the decision is still there)*
> You: "A clean approval is written into an append-only ledger, and it
> survives a refresh — because the ledger *is* the state. Underneath is
> a real MCP server — spec 2025-11-25, Streamable HTTP — the surface
> Alexa+ connects to. Every answer in this demo was a live tool call;
> the trace chips are still on screen."

**[2:12 — back to the full board for the close]**
> You: "Every agent fleet is going to need this: status that separates
> claims from verified facts, and a human gate that can't be redirected.
> Ask ABUZ8. Claimed is not done — verified is."

**[2:30 — stop.]**

## If something goes sideways mid-take

- **Page shows DEMO MODE instead of LIVE:** the server window died —
  the console has already fallen back to a labeled in-page port of the
  same rules (hash-bound decisions and tamper-voids included). Either
  keep rolling — the story is identical — or restart the server
  (command above), refresh, and pick up from the last beat.
- **Speech recognition is flaky:** ignore the mic; the chips and buttons
  are the demo path. Nothing changes.
- **You already decided an approval in a rehearsal:** delete
  `data/feed.runtime.json`, restart the server, refresh — pristine
  again. (In DEMO MODE, use the reset chip on the page.)
- **Running long:** cut the drill-down beat [0:25]. The board, the
  tamper refusal, and the ledger close carry the story.
