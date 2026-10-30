# NEXT.md — Ask ABUZ8 v1.1 ideas (not v1 scope)

- Stable public hostname for `/mcp` (named Cloudflare tunnel or VPS per HOSTING.md), then swap `YOUR-MCP-ENDPOINT` in `alexa/skill-manifest.json` and paste the URL into SUBMISSION.md.
- Record the demo video from DEMO-SCRIPT.md (2:30, one take) and attach it to the Devpost submission.
- Root-cause the cloudflared quick-tunnel edge 404s seen from this network (tunnel registers, edge never routes; zero requests arrived) — or just use a named tunnel.
- Create the GitHub Release for v1.0.0 with the demo video attached (tag exists; `gh` release is the remaining click).
- Wire the APL approval card's live datasource once an Alexa+ Agent Skill slot is granted (sample A-201 datasource ships in the doc today).
- Consider `pip --upgrade` noise: fresh venvs print a pip-update notice; harmless, ignore unless it confuses judges.
