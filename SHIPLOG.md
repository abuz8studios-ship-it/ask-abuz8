# SHIPLOG.md — Ask ABUZ8

✅ Ask ABUZ8 v1.0.0 — DONE
WHAT:     Voice concierge (Alexa+ track) over an ISNAD ledger: claimed-vs-verified mission status and hash-bound Tier-3 approvals, served by a self-hosted MCP server (spec 2025-11-25, Streamable HTTP) + simulated console + Alexa skill package.
USE IT:   git clone https://github.com/abuz8studios-ship-it/ask-abuz8.git → pip install -r requirements.txt → python mcp_server/server.py → http://127.0.0.1:8377/ (or: docker build -t ask-abuz8 . && docker run -p 127.0.0.1:8377:8377 -v ask-abuz8-data:/app/data ask-abuz8)
PROOF:    clean GitHub clone + README install → 22/22 core checks [live-probed] → MCP smoke incl. 2025-11-25 negotiation + Host 200/421 [live-probed] → live core flow: M-102 never done, tamper VOID, clean approve persists across restart [live-probed] → docker build/run + volume persistence across recreate [live-probed] → proxied public Host serves, evil Host 421 [live-probed] → no TODOs/secrets; placeholders all declared [verified]
UPDATE:   edit → tests/test_core.py + tests/smoke_mcp.py green → git commit → git push origin main → move tag: git tag -f vX.Y.Z && git push -f origin vX.Y.Z
BLOCKERS: none (quick-tunnel leg environment-blocked on this network; named-tunnel/VPS path documented in HOSTING.md and proxied-Host behavior proven locally)
NEXT:     record the DEMO-SCRIPT.md video; stand up the stable public hostname (see NEXT.md)
