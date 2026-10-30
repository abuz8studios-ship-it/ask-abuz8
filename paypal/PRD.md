# PRD — Ask ABUZ8 + PayPal (PayPal AI Hackathon, $67.5K)

**One-line product definition:** the ONE Ask core, able to actually charge for a
service — Ask ABUZ8 with a meaningful PayPal Sandbox checkout wired in: an agent
that sells, not just answers.

## The offer being sold
LotVue360 — Dealer Plan, USD 99.00/mo, first 5 vehicles free. A real ABUZ8 offer
with a live Stripe payment link in production since Oct 27, 2026; PayPal becomes
the parallel rail for this entry. One payer, one price, no new system.

## The flow (what a judge does)
1. Open the hosted demo. Ask ABUZ8 answers live (Nemotron via Token Factory).
2. Ask about the Dealer Plan — the agent presents the offer.
3. Press "Ask the agent to check me out" (or tell the agent you want it).
   The agent confirms the offer in words; the server creates a PayPal Sandbox
   order at the catalog price and returns the PayPal approve link.
4. Approve in PayPal Sandbox (buyer sandbox account) → return to the app →
   the app captures the order and shows the verified capture (order id, status,
   capture id). No real money moves at any point.

## The design rule that makes it "meaningful" (ISNAD applied to money)
The model can PRESENT the offer; it can never SET the price. The price lives in
a server-side catalog constant and is the only value that reaches PayPal.
Claimed (what the agent says) is checked against Verified (what the server
charges) — the same isnad discipline the fleet runs on, applied to a checkout.

## Non-goals
- No live payments (Sandbox only, per the hackathon's rules).
- No subscriptions/recurring billing in v1 (one-time capture of the first month).
- No new agent system — an adapter on the existing Ask core.

## Deliverables (per the verified submission anatomy)
Registered Devpost project · public repo with license · working hosted demo ·
demo video < 3 minutes · description. Registration DONE Oct 30, 2026.
**File-by: Nov 9, 2026 (Ahmad's three-day rule; hard close Nov 12, 15:00 ET).**
