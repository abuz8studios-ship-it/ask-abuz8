# SHIPLOG.md — Ask ABUZ8

✅ Ask ABUZ8 v1.0.0 — DONE
WHAT:     Voice concierge (Alexa+ track) over an ISNAD ledger: claimed-vs-verified mission status and hash-bound Tier-3 approvals, served by a self-hosted MCP server (spec 2025-11-25, Streamable HTTP) + simulated console + Alexa skill package.
USE IT:   git clone https://github.com/abuz8studios-ship-it/ask-abuz8.git → pip install -r requirements.txt → python mcp_server/server.py → http://127.0.0.1:8377/ (or: docker build -t ask-abuz8 . && docker run -p 127.0.0.1:8377:8377 -v ask-abuz8-data:/app/data ask-abuz8)
PROOF:    clean GitHub clone + README install → 22/22 core checks [live-probed] → MCP smoke incl. 2025-11-25 negotiation + Host 200/421 [live-probed] → live core flow: M-102 never done, tamper VOID, clean approve persists across restart [live-probed] → docker build/run + volume persistence across recreate [live-probed] → proxied public Host serves, evil Host 421 [live-probed] → no TODOs/secrets; placeholders all declared [verified]
UPDATE:   edit → tests/test_core.py + tests/smoke_mcp.py green → git commit → git push origin main → move tag: git tag -f vX.Y.Z && git push -f origin vX.Y.Z
BLOCKERS: none (quick-tunnel leg environment-blocked on this network; named-tunnel/VPS path documented in HOSTING.md and proxied-Host behavior proven locally)
NEXT:     record the DEMO-SCRIPT.md video; stand up the stable public hostname (see NEXT.md)

✅ Ask ABUZ8 Portable v1.2.0 — DONE
WHAT:     USB-stick appliance: frozen MCP server + console + sample ledger + double-click launcher, no Python/install/network needed.
USE IT:   https://github.com/abuz8studios-ship-it/ask-abuz8/releases → Ask-ABUZ8-Portable-win64.zip → unzip → Start-Ask-ABUZ8.bat
PROOF:    zip built by appliance/build_appliance.ps1 [live-probed] → extracted fresh from zip: full 7-step flow incl. tamper-void on frozen exe [live-probed] → decisions persist across relaunch [live-probed] → --fresh resets to pristine [live-probed] → history+bundle secret scan clean (1 explained OpenSSL-label FP) [verified] → pip-audit zero vulns [live-probed]
UPDATE:   edit → suites green → appliance/build_appliance.ps1 → extract+smoke → gh release upload → commit+push+tag
BLOCKERS: none (unsigned exe: SmartScreen "More info → Run anyway" documented in appliance README; clean-machine test is Ahmad's)
NEXT:     demo video; stable public endpoint; signed build (see NEXT.md)

✅ Ask ABUZ8 CI+Pipeline v1.3.0 — DONE
WHAT:     Every push CI-greens 22 checks + MCP smoke on Windows+Linux; every tag auto-builds the portable appliance on a clean runner and attaches zip+sha to the release.
USE IT:   push → https://github.com/abuz8studios-ship-it/ask-abuz8/actions ; tag vX.Y.Z → release appears with artifacts
PROOF:    ubuntu+windows legs green from CI logs (22/22 + smoke each) [live-probed] → v1.3.0 job built 14.9MB zip on clean runner in 74s [live-probed] → downloaded zip matches published sha256 exactly [live-probed] → extracted CI zip booted, full 7-assertion flow green [live-probed] → workflows secret-free (GITHUB_TOKEN context only) [verified]
UPDATE:   edit workflows → push → watch gh run list → tag to ship
BLOCKERS: none
NEXT:     web-live hosting (Ahmad's Cloudflare go-ahead), mobile wrapper after that (see NEXT.md)

✅ Ask ABUZ8 Steady-State (ahmad audit) — DONE
WHAT:     Full re-probe: every shipped surface re-verified, last two untested branches closed (start.sh on real Linux, .bat py-fallback on real misfire), one doc drift fixed.
USE IT:   unchanged — repo, starters, appliance zip, CI pipeline (see stanzas above)
PROOF:    22/22 + smoke local [live-probed] → CI 4/4 incl. prior unwatched run [live-probed] → start.sh end-to-end on Debian (apt→venv→boot→/health→/→MCP) [live-probed] → .bat fallback fired on real py failure, fresh venv served, dev venv restored intact [live-probed] → live demo untouched throughout [live-probed] → HOSTING FASTMCP row corrected to disk truth [verified]
UPDATE:   same as v1.3.0 stanza
BLOCKERS: none (WSL Ubuntu VHD missing on this box — Debian used instead; start.sh unaffected)
NEXT:     web-live hosting (Ahmad's go-ahead), demo video, submitted-yes/no answer
