# Hosting Ask ABUZ8 — a public Streamable HTTP endpoint

The MCP server is the product surface: Alexa+ (and any MCP client) connects
to one public **HTTPS** URL, `https://<your-host>/mcp`. The same process
also serves the simulated experience at `/` and a health check at
`/health`. This document takes the server from a laptop to that URL three
ways — container, tunnel, bare VPS — with honest placeholders: **no public
hostname exists yet**; wherever you see `YOUR-HOST` or `mcp.example.com`,
substitute the real one you create, then paste it into `SUBMISSION.md` and
into the `https://YOUR-MCP-ENDPOINT/mcp` slots in
`alexa/skill-manifest.json`.

## Environment variables

| Variable | Default | What it does |
|---|---|---|
| `PORT` | `8377` | Port the server listens on. |
| `ASK_ABUZ8_FEED` | `data/feed.runtime.json` | Ledger file. Auto-seeded from `data/feed.json` on first run; decisions append here. Point it at the production company feed to run live. |
| `ASK_ABUZ8_ALLOWED_HOSTS` | _(unset)_ | Public hostname(s) accepted on `/mcp` behind a proxy/tunnel (comma-separated, bare hosts or full URLs). **Required for public exposure** — without it the SDK answers proxied calls with `421 Invalid Host header`. Localhost stays allowed either way. |
| `FASTMCP_HOST` | `127.0.0.1` | Bind address. `server.py` forwards this var into the FastMCP constructor (SDK defaults would otherwise shadow it), so containers set it to `0.0.0.0` **inside** the container (the `Dockerfile` does this). On a bare host, leave it on loopback and let the proxy forward. |

State note: the transport is stateless HTTP with JSON responses — any
process can serve any request — but the *ledger file is the state*.
Run one instance against one feed file (or one volume), and back the file
up; deleting `feed.runtime.json` resets the demo.

## Health check

```bash
curl https://YOUR-HOST/health
# ask-abuz8 mcp server: ok
```

Protocol check (proves spec negotiation, mirrors `tests/smoke_mcp.py`):

```bash
curl -s https://YOUR-HOST/mcp -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{
        "protocolVersion":"2025-11-25","capabilities":{},
        "clientInfo":{"name":"curl-check","version":"1"}}}'
# -> result.protocolVersion == "2025-11-25"
```

## Option A — Docker behind a TLS reverse proxy (the production shape)

```bash
docker build -t ask-abuz8 .
docker run -d --name ask-abuz8 --restart unless-stopped \
  -p 127.0.0.1:8377:8377 -v ask-abuz8-data:/app/data ask-abuz8
```

The port is published to the host's **loopback only**; the proxy owns the
public face and the TLS certificate (Alexa endpoints require HTTPS with a
publicly trusted cert).

Caddy (automatic HTTPS):

```caddyfile
mcp.example.com {
    reverse_proxy 127.0.0.1:8377
}
```

…or nginx:

```nginx
server {
    listen 443 ssl;
    server_name mcp.example.com;
    ssl_certificate     /etc/letsencrypt/live/mcp.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/mcp.example.com/privkey.pem;
    location / {
        proxy_pass http://127.0.0.1:8377;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_http_version 1.1;
        proxy_buffering off;          # Streamable HTTP friendly
    }
}
```

## Option B — Tunnel (fastest path for a judging demo)

No server, no DNS: run the server locally and expose it through a tunnel.

```bash
.venv/bin/python mcp_server/server.py                 # listens on 127.0.0.1:8377
cloudflared tunnel --url http://127.0.0.1:8377        # or: ngrok http 8377
# -> https://<random-name>.trycloudflare.com
# and restart the server with that name allowlisted:
#   ASK_ABUZ8_ALLOWED_HOSTS=<random-name>.trycloudflare.com .venv/bin/python mcp_server/server.py
```

Your endpoint is `https://<random-name>.trycloudflare.com/mcp` and the
simulator is at the tunnel root. **Honest caveat:** free tunnel URLs
change on every restart — fine for a demo window, wrong for a listing you
leave up. For a stable name, use a named Cloudflare tunnel with your own
domain, which is Option A with extra steps.

## Option C — Bare VPS, no Docker

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
PORT=8377 .venv/bin/python mcp_server/server.py       # loopback bind
```

Run it under your init system (systemd unit with `Restart=always`,
`Environment=PORT=8377`, `WorkingDirectory=` this repo), then put the same
reverse proxy from Option A in front. Identical exposure, one less layer.

## Security posture — read before you expose it

- **The demo server has no authentication of its own.** That is a demo
  property, stated plainly. The hash-bound approvals protect *decision
  integrity* (nobody can redirect a decision to a payload the owner didn't
  see) — they do not gate *who can call the endpoint*. Before any
  production exposure, put the proxy to work: require a shared secret
  header or mTLS at the proxy, and/or IP-allowlist the callers you expect
  (Alexa service endpoints, your own console).
- Keep the bind tight: loopback on the host, `0.0.0.0` only inside the
  container's private network. Never publish the raw port publicly.
- The SDK rejects `/mcp` calls whose Host header is not allowlisted (`421`, DNS-rebinding protection):
  set `ASK_ABUZ8_ALLOWED_HOSTS` to your public hostname(s); the allowlist always
  keeps localhost, and loopback binds stay strict when the variable is unset.
- The ledger is append-only and decisions are one-way by design. If a
  decision ever needs to be *countermanded*, that is a new operational
  event in your process — the code deliberately offers no undo.

## Go-live checklist

1. Pick a topology (A/B/C), set `ASK_ABUZ8_ALLOWED_HOSTS` to your public hostname, and stand the server up.
2. `curl https://YOUR-HOST/health` → `ok`; run the initialize check above.
3. Open `https://YOUR-HOST/` — the mission-control console should show
   **LIVE · MCP SERVER** in the top bar (it falls back to a labeled
   DEMO MODE if the server is unreachable, which is your tell that the
   proxy is misrouting `/mcp`).
4. Make one approval decision from the console; restart the server;
   confirm the decision persisted (the ledger file is the state).
5. Paste the final `/mcp` URL into `SUBMISSION.md` and replace every
   `https://YOUR-MCP-ENDPOINT/mcp` in `alexa/skill-manifest.json`.
