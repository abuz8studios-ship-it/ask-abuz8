# Ask ABUZ8 — Portable Appliance

The voice concierge that never calls a claim "done" — as a folder that runs
on any Windows 10/11 PC. No Python, no install, no network needed.

## Run it

1. Unzip `Ask-ABUZ8-Portable-win64.zip` anywhere (Desktop is fine).
2. Double-click **`Start-Ask-ABUZ8.bat`**.
3. The console opens in your browser. Click the chips: company status →
   *what is still only claimed* → approvals → **TAMPER TEST**.
4. Close the "Ask ABUZ8 Appliance" window to stop it.

First launch may show Windows SmartScreen ("Windows protected your PC") —
this v1 build is unsigned. Click **More info → Run anyway**. (Signing is
on the roadmap; the code is public and the zip hash is published on the
release page so you can verify the download.)

To reset the demo: `Start-Ask-ABUZ8.bat --fresh` (wipes decisions, restores
the pristine sample ledger).

## Owner mode (your live company feed)

By default the appliance runs the bundled **sample ledger**. To point it at
a live company feed, edit `config\feed.txt`: put the feed file path on the
first line that does not start with `#`, then start normally.

## Troubleshooting

- **Port busy?** Another copy may be running. Or set another port first:
  open a terminal here and run `set PORT=8390 && Start-Ask-ABUZ8.bat`.
- **Console shows DEMO MODE?** The server window died — restart the .bat.
  (DEMO MODE is the same rules running in-page; nothing breaks, but LIVE
  is the real server.)
- **Something looks wrong?** The appliance window shows the server log.

## What is inside

`Ask-ABUZ8.exe` (+ `_internal/`) is the frozen MCP server (spec 2025-11-25):
`simulator/` the console, `data/feed.json` the sample-ledger seed, `data/`
where your decisions persist. Source + build script:
https://github.com/abuz8studios-ship-it/ask-abuz8 (see `appliance/`).
