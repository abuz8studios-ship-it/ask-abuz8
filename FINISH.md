FINISH LINE:   A stranger can clone ask-abuz8, install with two README commands, pass 22 core checks + the MCP 2025-11-25 smoke test, start one server process, and run the full voice-concierge demo (live ISNAD board, approvals, tamper-void) in a browser.
TARGET:        Public GitHub repo (source) + Docker image (artifact) + demo video path (DEMO-SCRIPT.md)
CORE FLOW:     (1) install deps (2) run tests green (3) start server (4) open console: LIVE pill, board renders (5) ask "what is still only claimed" -> M-102, NOT done (6) tamper test -> server refuses + voids (7) clean approve -> ledger entry persists across restart
MONEY PATH:    n/a (hackathon entry; no checkout)
OUT OF SCOPE:  Alexa+ Agent Skill provisioning (Amazon program, no self-serve on-ramp); physical Echo device; stable public hostname (tunnel/VPS is judge's choice per HOSTING.md); live production-feed wiring (env var documented, sample feed ships)
