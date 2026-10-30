# SPEC.md — Ask ABUZ8 Portable Appliance v1

**What:** a USB-stick appliance: one folder that runs the Ask ABUZ8 voice
concierge on any Windows 10/11 PC with no Python, no install, no network.
Double-click → console opens with LIVE pill → full demo (board, approvals,
tamper test) works offline.

**Who:** agent-fleet owners (Ahmad first, then anyone who downloads the zip);
evaluators who refuse to set up toolchains.

**Core flow (3 steps):** (1) unzip, double-click `Start-Ask-ABUZ8.bat`;
(2) console opens, board renders from the bundled sample ledger;
(3) chips carry the story: status → still-only-claimed → approvals →
tamper-void → clean approve persists in `data/feed.runtime.json`.

**Stack (locked):** PyInstaller one-dir (`Ask-ABUZ8.exe` + `_internal/`),
spec at `appliance/Ask-ABUZ8.spec`, builder `appliance/build_appliance.ps1`
(house pattern from `ABUZ8_PORTABLE`), output `dist-appliance/` (gitignored).
Data stays EXTERNAL (writable ledger, swappable feed): `simulator/`,
`data/feed.json` seed, `config/feed.txt` owner override. One 3-line
frozen-aware `ROOT` touch in `mcp_server/server.py`; no other core changes.

**Data schema:** unchanged — append-only `feed.json` events; runtime ledger
`data/feed.runtime.json` seeded on first boot; `config/feed.txt` (optional)
holds a path that the launcher exports as `ASK_ABUZ8_FEED`.

**Private routes:** none new — loopback-only server, same as repo. No auth
in the appliance (documented; physical-access threat model).

**OUT OF SCOPE v1:** macOS/Linux binaries, single-file exe, installer,
auto-update, cloud hosting, Alexa provisioning, any core behavior change.
