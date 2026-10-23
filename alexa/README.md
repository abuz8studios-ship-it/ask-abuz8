# Ask ABUZ8 — Alexa skill configuration package

This folder is the **Alexa-facing configuration** for Ask ABUZ8: everything
Amazon's side would need to provision the skill, written against the same
interaction model and the same MCP server that ship in this repository.

**Honest status, up front.** Alexa+ Agent Skill provisioning runs through
Amazon's own program; there is no self-serve on-ramp (that gap is in the
submission's friction log). The hackathon entry therefore runs on the two
paths the rules provide — the self-hosted **MCP server**
(`../mcp_server/server.py`, spec 2025-11-25, Streamable HTTP) and the
**simulated Alexa+ experience** (`../simulator/index.html`). This package is
the deploy-ready configuration for the day an Agent Skill slot is granted:
the interaction model here is the *same model* the simulator runs
(`../simulator/intents.json`), so nothing about the conversation changes —
only the surface that hosts it.

## Files

| File | What it is |
|---|---|
| `skill-manifest.json` | Alexa skill manifest (schema 1.0): publishing info for en-US, the custom API endpoint block, APL interface declaration, privacy/compliance answers (no purchases, no personal info, not child-directed). |
| `interaction-model.json` | The full en-US interaction model in Alexa JSON format: invocation name `ask a b u z 8`, 7 custom intents (8–12 utterances each), 2 slot types, and the standard `AMAZON.*` built-ins. |
| `apl/approval-card.json` | An Alexa Presentation Language document (APL 2023.3, dark theme) that renders a Tier-3 approval on Echo Show: action, requester, the exact payload flattened to rows, the SHA-256 (short + full), and touchable Approve / Deny that fire `SendEvent` with the decision arguments. Its datasource is **sample data** (action A-201 from `data/feed.json`, with the payload's real hash) — at runtime the skill service injects the live `pending_approvals` output. |
| `README.md` | This file. |

## How the skill maps onto the MCP server

Intents map **1:1** onto MCP tools — the same mapping the simulator uses.
The skill service is a thin translator: it turns an intent into a
`tools/call`, and speaks the tool's `say` field back.

| Intent | MCP tool | Notes |
|---|---|---|
| `CompanyStatusIntent` | `company_status` | ISNAD roll-up by state + pending count. |
| `MissionStatusIntent` `{MissionId}` | `mission_status` | Claimed vs verified, with evidence. |
| `AllMissionsIntent` | `mission_status` (no id) | The whole board. |
| `UnverifiedClaimsIntent` | `unverified_claims` | CLAIMED ≠ DONE — the signature question. |
| `PendingApprovalsIntent` | `pending_approvals` | On a screen device, also render `apl/approval-card.json` with the first pending approval as its datasource. |
| `ApproveIntent` `{ActionId?}` | `decide_approval` (`APPROVED`) | See the hash rule below. |
| `DenyIntent` `{ActionId?}` | `decide_approval` (`DENIED`) | Same hash rule. |

**The hash rule (the point of the whole product).** `decide_approval`
requires `payload_hash` — the SHA-256 of the exact payload that was
*presented*. A voice user never speaks a hash. The skill service keeps the
presented approval in session attributes (set by `PendingApprovalsIntent`,
or by whichever turn rendered the APL card) and passes that stored hash
verbatim with the decision. If the payload was edited after presentation,
the hash the owner "saw" no longer matches the payload on record: the
server **refuses the decision and voids the request**. Touch input follows
the same path — the APL card's `SendEvent` carries
`[decide_approval, decision, actionId, payloadHash]` and the service
forwards them unchanged.

**APL specifics.** The card declares no external assets and no imports —
pure core components (`Container`, `Text`, `TouchWrapper`, `SendEvent`),
so it renders on any APL 1.x+ device. Payload rows come from
`approval.payloadLines` (the payload object flattened by the service);
`shortHash` / `payloadHash` come straight from the `pending_approvals`
tool output.

## Deploy checklist

1. **Host the MCP server publicly over HTTPS** — see `../HOSTING.md`.
   Alexa endpoints must be HTTPS with a publicly trusted certificate.
2. **Replace the endpoint placeholder.** In `skill-manifest.json`, every
   `https://YOUR-MCP-ENDPOINT/mcp` (custom API endpoint + NA region +
   events endpoint) becomes your real public `/mcp` URL.
3. **Replace the publishing placeholders** (all marked `REPLACE_ME_`):
   icon URIs (108×108 and 512×512 PNG), privacy-policy and terms-of-use
   URLs, and the testing instructions if your test data differs.
4. **Create the skill** in the Alexa developer console (or ASK CLI),
   paste/import `skill-manifest.json`, and set the interaction model
   from `interaction-model.json` (Build → Interaction Model → JSON editor).
5. **Declare the APL interface** (already in the manifest's
   `apis.custom.interfaces`) so screen devices can render the approval card,
   and wire the `PendingApprovalsIntent` response to attach the APL
   `RenderDocument` directive with `apl/approval-card.json`.
6. **Smoke-test in the Alexa simulator** with the manifest's testing
   instructions: status → unverified claims → approvals → approve, then
   re-present an edited payload and confirm refusal + void.
7. **Certification notes to honor:** the skill collects no personal info,
   makes no purchases, and is not child-directed (already reflected in
   `privacyAndCompliance`). Approval decisions are one-way and permanent
   by design — say so in the skill description (it already does).

## Placeholders — the complete, honest list

- `YOUR-MCP-ENDPOINT` in `skill-manifest.json` — no public hostname is
  claimed anywhere in this repo; see `../HOSTING.md` for how to create one.
- `REPLACE_ME_` icon, privacy, and terms URLs, and the testing-instructions
  prefix in the manifest.
- The APL `datasources.approval` block — sample A-201 data with its real
  hash, present so the document renders in the APL authoring tool as-is.
- `MISSION_ID` / `ACTION_ID` slot values mirror the sample feed
  (`M-101`–`M-104`, `A-201`–`A-202`); against the live company feed the
  service resolves ids dynamically and the slot lists are illustrative.

Nothing in this package talks to a physical Alexa device today, and it does
not pretend to: it is the configuration half of the entry, deploy-ready for
Amazon's provisioning, with the working half (MCP server + simulated
experience) already live in this repo.
