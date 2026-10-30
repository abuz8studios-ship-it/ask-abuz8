# FILING SHEET — PayPal AI Hackathon ($67.5K)

Hard close: **Thu Nov 12, 2026, 15:00 ET** · **FILE-BY: Mon Nov 9, 2026** (three-day rule)
Event: paypalaihackathon.devpost.com · Devpost user: abuz8studios

## Status
- [x] **Registration** — DONE + verified on screen Oct 30, 2026 ("Thanks for registering!", solo).
- [x] **PRD** — PRD.md (this pack).
- [x] **App scaffold** — app.py: Ask core + agent checkout + PayPal Sandbox Orders v2
      (create → approve → capture), server-side price catalog. Smoke-tested locally
      (health / page / honest 503 without creds / live chat) — see build log below.
- [ ] **Devpost project** — create under the PayPal hackathon ("Start a Project").
      BLOCKED on a signed-in Devpost session: the saved vault password was rejected
      Oct 30 (Kiroween attempt). Retry route: "Log in with Google". The SAME retry
      unblocks the Kiroween registration.
- [ ] **PayPal Sandbox app** — Developer Dashboard → create sandbox app → client id +
      secret go to the Secure Vault (NEVER chat). Then set env on the host and run
      one full sandbox purchase end-to-end (test buyer) as the verification snap.
- [ ] **Public repo** — publish this pack (MIT LICENSE included) to GitHub
      (abuz8studios-ship-it), OSI license visible in About.
- [ ] **Hosted demo** — public door decision pending. Candidates: HF Space (needs a
      billing tap — CPU upgrade/PRO), Cloudflare Worker front, Modal endpoint.
      Pegasus is OUT (home power down, Oct 30).
- [ ] **Demo video < 3:00** — record off the hosted demo (agent checkout + sandbox
      approve + capture), narrated; public YouTube.
- [ ] **Submit + verify submitted state on screen** — before Nov 9.

## Build log
- 2026-10-30 ~14:35 ET — pack created (app.py, PRD.md, README.md, LICENSE, this sheet).
- 2026-10-30 ~14:40 ET — SMOKE TEST PASSED locally on the VM: py_compile OK;
  /health {ok, model, sandbox, paypal_configured:false}; page HTTP 200;
  create-order without creds → honest 503; live chat → real Nemotron answer
  with correct plan facts ($99.00/mo, first 5 vehicles free).
