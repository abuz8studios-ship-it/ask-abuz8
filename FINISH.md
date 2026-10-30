FINISH LINE:   Ask ABUZ8 ships everywhere it can with zero new accounts: every push CI-greens the 22 checks + MCP smoke on Windows+Linux, and every tag auto-builds the portable appliance and attaches it to the release.
TARGET:        GitHub CI (test matrix) + tag-triggered appliance release pipeline
CORE FLOW:     (1) push → CI green (2) tag vX.Y.Z → release job builds zip on a clean runner (3) zip+sha attached to release (4) download verified byte-identical
MONEY PATH:    n/a (free/open-source; no checkout)
OUT OF SCOPE:  web-live hosting (needs Ahmad's Cloudflare/DNS go-ahead), mobile wrapper (needs web-live URL first), signed builds (needs cert), installer
