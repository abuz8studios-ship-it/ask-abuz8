# Friction log — Ask ABUZ8 (Build, Ship, Shape)

Format per entry: task attempted · steps · expected vs. actual · severity ·
workaround · actionable suggestion.

## 1. MCP Python SDK v2 renamed its server API
- **Task:** set up the Alexa+ MCP server from the official Python SDK.
- **Steps:** `pip install mcp`, then followed the widely documented v1
  pattern: `from mcp.server.fastmcp import FastMCP`.
- **Expected vs. actual:** expected the import to work. Actual:
  `ModuleNotFoundError` — SDK v2 renamed FastMCP to `MCPServer`
  (`mcp.server.mcpserver`) and changed other APIs, so current-install +
  documented-code disagree.
- **Severity:** Medium (blocked the build until diagnosed).
- **Workaround:** pinned `mcp<2` → installed 1.30.0, whose
  `LATEST_PROTOCOL_VERSION` is exactly `2025-11-25`, the spec version the
  Alexa+ track requires.
- **Suggestion:** put a "known-good versions" note on the Alexa+ resources
  page ("Python: mcp 1.30.x negotiates spec 2025-11-25"), and ask the SDK
  team for a compatibility shim or louder migration warning at import time.

## 2. The $150 AWS promotional-credit path was already closed
- **Task:** claim the hackathon's $150 AWS promotional credits to host the
  MCP server the way a judge would run it.
- **Steps:** read the official rules' credit section and followed the
  linked Google form.
- **Expected vs. actual:** expected an open request path during the
  submission period. Actual: the form's deadline was Oct 21, 12pm PT, and
  an Oct 7 update in the rules says credit codes are exhausted. The main
  page still reads as if credits are part of the offer.
- **Severity:** Low for this project (see workaround), High for entrants
  whose builds need paid AWS services to exist at all.
- **Workaround:** built the entire submission to run locally at $0 — the
  MCP server is a single Python process a judge can start in two commands.
- **Suggestion:** when a benefit closes mid-hackathon, say so on the main
  hackathon page, not only inside the rules text.

## 3. No self-serve Alexa+ Agent Skill on-ramp found
- **Task:** evaluate the "Agent Skill" path for the Alexa+ track.
- **Steps:** followed the hackathon Resources and the rules' "How To
  Enter" links for Alexa+.
- **Expected vs. actual:** expected a developer on-ramp comparable to the
  MCP one (the rules link straight to modelcontextprotocol.io). Actual:
  the linked path leads to MCP documentation; I found no equivalent
  zero-to-hello-world for provisioning an Alexa+ Agent Skill as an
  independent developer inside the hackathon window.
- **Severity:** Medium (shaped the whole architecture — fortunately the
  rules anticipate this).
- **Workaround:** took the two paths the rules explicitly provide: a
  self-hosted MCP server (spec 2025-11-25, Streamable HTTP) plus the
  simulated Alexa+ experience in a web app.
- **Suggestion:** one page — "Alexa+ Agent Skills for independent
  developers: who can provision what, and how" — linked from the track
  description, even if the honest answer today is "start with MCP."
