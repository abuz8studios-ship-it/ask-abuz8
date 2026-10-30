# Ask ABUZ8 + PayPal

Ask ABUZ8 — the front door of ABUZ8 LLC — with a working PayPal Sandbox
checkout: an agent that sells, not just answers. Built for the PayPal AI
Hackathon by Ahmad Odeh / ABUZ8 LLC.

The agent presents the LotVue360 Dealer Plan (USD 99.00/mo, first 5 vehicles
free — a real ABUZ8 offer, live on Stripe since Oct 27, 2026). When a buyer
accepts, the server creates a PayPal Sandbox order at the catalog price,
the buyer approves in PayPal, and the app captures and shows the verified
result. **The model never sets the price** — the price is a server-side
catalog constant; that separation (claimed vs. verified) is the same ISNAD
discipline the whole ABUZ8 fleet runs on.

## Run it

```bash
export PAYPAL_CLIENT_ID=<sandbox app client id>
export PAYPAL_CLIENT_SECRET=<sandbox app secret>
export PAYPAL_ENV=sandbox
export NEBIUS_API_KEY=<token factory key>        # the Ask model's key
export PUBLIC_BASE_URL=https://your-host.example # PayPal return/cancel base
python3 app.py                                   # serves on PORT (default 8901)
```

Stdlib-only Python 3 — no dependencies.

## Endpoints

- `GET /` — demo page (chat + agent checkout)
- `GET /health` — liveness + whether PayPal Sandbox is configured
- `POST /api/chat` — `{message}` → Ask ABUZ8 reply (Nemotron-3-Nano-30B-A3B via Nebius Token Factory)
- `POST /api/agent/checkout` — agent confirms the offer + creates the Sandbox order → `{reply, order_id, approve_url}`
- `POST /api/paypal/create-order` — order only → `{order_id, approve_url}`
- `GET /paypal/return?token=<orderId>` — captures the order, shows the verified capture
- `GET /paypal/cancel` — buyer cancelled; no charge

## Prior work note

The Ask ABUZ8 core predates this hackathon (built for earlier events, incl.
the Amazon Build/Ship/Shape entry and the Nebius × NVIDIA entry). The new
work for this hackathon is the PayPal selling flow: the server-side catalog,
the agent checkout endpoint, and the Sandbox Orders v2 create → approve →
capture integration.

## License

MIT — see LICENSE.
