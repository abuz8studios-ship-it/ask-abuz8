#!/usr/bin/env python3
"""Ask ABUZ8 + PayPal — PayPal AI Hackathon entry.

The ONE Ask core (Ask ABUZ8), now able to charge for a service:
an agent that sells, not just answers. The agent presents the offer,
the price is verified server-side (ISNAD: the model never sets the
price), and checkout runs through the PayPal Sandbox Orders v2 API.

Credentials (env vars, never in code, never in chat):
  NEBIUS_API_KEY        — Token Factory key for the Ask model.
                          Local dev inside the Muse VM falls back to
                          the custom-connector surrogate helper.
  PAYPAL_CLIENT_ID      — PayPal Sandbox app client id.
  PAYPAL_CLIENT_SECRET  — PayPal Sandbox app secret.
  PAYPAL_ENV            — "sandbox" (default) or "live".
  PUBLIC_BASE_URL       — public origin of this app, used for the
                          PayPal return/cancel URLs.
  PORT                  — default 8901.
"""
import base64
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------- Ask core
BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"  # verified live 2026-10-30
PORT = int(os.environ.get("PORT", "8901"))
PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "").rstrip("/")

SYSTEM_PROMPT = (
    "You are Ask ABUZ8, the front door of ABUZ8 LLC — a one-person AI company run "
    "by a fleet of autonomous agents. Your rule is ISNAD: a claim is not a fact. "
    "You separate what is CLAIMED from what is VERIFIED, and money-out, publishing, "
    "and irreversible actions always wait for the owner's approval. "
    "You can also sell one verified offer: the LotVue360 Dealer Plan at exactly "
    "USD 99.00 per month (first 5 vehicles free). When a buyer wants it, confirm "
    "the offer in one short paragraph; the checkout itself is created server-side "
    "at the verified price — you never invent or change prices, discounts, or terms. "
    "Answer concisely, concretely, and honestly. If you do not know, say so."
)

# The verified catalog. Server-side only: this is the price that reaches
# PayPal, whatever the model or the browser says.
CATALOG = {
    "lotvue360-dealer": {
        "name": "LotVue360 — Dealer Plan",
        "description": "LotVue360 Dealer Plan — dealer photo-to-360 listing service (PayPal Sandbox demo charge)",
        "price": "99.00",
        "currency": "USD",
    }
}

# ---------------------------------------------------------------- PayPal
PAYPAL_ENV = os.environ.get("PAYPAL_ENV", "sandbox").lower()
PAYPAL_BASE = (
    "https://api-m.sandbox.paypal.com"
    if PAYPAL_ENV != "live"
    else "https://api-m.paypal.com"
)


def paypal_configured():
    return bool(os.environ.get("PAYPAL_CLIENT_ID") and os.environ.get("PAYPAL_CLIENT_SECRET"))


def paypal_access_token():
    cid = os.environ["PAYPAL_CLIENT_ID"]
    secret = os.environ["PAYPAL_CLIENT_SECRET"]
    basic = base64.b64encode((cid + ":" + secret).encode()).decode()
    req = urllib.request.Request(
        PAYPAL_BASE + "/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": "Basic " + basic,
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))["access_token"]


def paypal_api(method, path, token, payload=None):
    req = urllib.request.Request(
        PAYPAL_BASE + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def create_paypal_order(item_key):
    """Create a Sandbox order at the server-verified catalog price.
    Returns (order_id, approve_url)."""
    item = CATALOG[item_key]
    token = paypal_access_token()
    base = PUBLIC_BASE_URL or ("http://127.0.0.1:" + str(PORT))
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [
            {
                "reference_id": item_key,
                "description": item["description"],
                "amount": {"currency_code": item["currency"], "value": item["price"]},
            }
        ],
        "application_context": {
            "brand_name": "ABUZ8 LLC",
            "user_action": "PAY_NOW",
            "return_url": base + "/paypal/return",
            "cancel_url": base + "/paypal/cancel",
        },
    }
    order = paypal_api("POST", "/v2/checkout/orders", token, payload)
    approve = None
    for link in order.get("links", []):
        if link.get("rel") == "approve":
            approve = link.get("href")
    if not approve:
        raise RuntimeError("PayPal order created without an approve link")
    return order["id"], approve


def capture_paypal_order(order_id):
    token = paypal_access_token()
    return paypal_api("POST", "/v2/checkout/orders/" + order_id + "/capture", token, {})


# ---------------------------------------------------------------- LLM
def apply_auth(req):
    key = os.environ.get("NEBIUS_API_KEY")
    if key:
        req.add_header("Authorization", "Bearer " + key)
        return
    # Local dev fallback: Muse VM surrogate exchange (never prints the key).
    sys.path.insert(0, "/opt/muse/skills/custom-connector-setup/bin")
    from dynamic_credentials import add_surrogate_to_request

    add_surrogate_to_request(req, "custom.nebius-token-factory",
                             allowed_hosts=["api.tokenfactory.nebius.com"])


def chat_completion(user_text):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        "max_tokens": 900,  # reasoning model: small budgets return empty content
        "temperature": 0.4,
    }
    req = urllib.request.Request(
        BASE_URL + "chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    apply_auth(req)
    with urllib.request.urlopen(req, timeout=120) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data["choices"][0]["message"]["content"], data.get("model", MODEL)


# ---------------------------------------------------------------- Page
PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ask ABUZ8 + PayPal — an agent that can charge for a service</title>
<style>
 body{background:#0b0f14;color:#e6edf3;font-family:Segoe UI,Arial,sans-serif;margin:0}
 .wrap{max-width:820px;margin:0 auto;padding:28px 20px 40px}
 h1{font-size:30px;margin:0 0 4px} .sub{color:#9fb0c3;margin:0 0 6px}
 .badge{display:inline-block;background:#12351f;color:#3fb96b;border:1px solid #3fb96b;border-radius:20px;padding:1px 10px;font-size:12px;font-weight:700}
 .card{background:#11161d;border:1px solid #26313f;border-radius:10px;padding:16px;margin:18px 0}
 #log{background:#11161d;border:1px solid #26313f;border-radius:10px;padding:16px;min-height:220px;margin:18px 0}
 .msg{margin:10px 0;line-height:1.5} .who{font-weight:700;font-size:12px;letter-spacing:.6px}
 .user .who{color:#6cb6ff} .bot .who{color:#ffb454}
 .row{display:flex;gap:8px} input{flex:1;background:#11161d;border:1px solid #26313f;border-radius:8px;color:#e6edf3;padding:11px 12px;font-size:15px}
 button{background:#1f6feb;border:0;color:#fff;border-radius:8px;padding:11px 18px;font-size:15px;cursor:pointer}
 .buy{background:#ffc439;color:#111;font-weight:700}
 .small{color:#9fb0c3;font-size:13px;margin-top:14px}
</style></head><body><div class="wrap">
<h1>Ask ABUZ8 <span style="color:#9fb0c3">+ PayPal</span></h1>
<p class="sub">The front door of a one-person AI company — an agent that can
<b>charge for a service</b> through PayPal Sandbox.</p>
<span class="badge">ASK CORE LIVE &middot; PAYPAL SANDBOX CHECKOUT</span>
<div class="card"><b>LotVue360 — Dealer Plan</b> &middot; USD 99.00/mo &middot; first 5 vehicles free<br>
<p class="small">Ask the agent about the plan, then let the agent create your
PayPal Sandbox checkout. The price is verified server-side — the agent can
present the offer, it can never change the price.</p>
<button class="buy" onclick="agentCheckout()">Ask the agent to check me out</button>
<span id="buyout" class="small"></span></div>
<div id="log"><div class="msg bot"><span class="who">ASK ABUZ8</span><br>Ask me about the Dealer Plan, the fleet, or how I keep agent claims honest — or hit the button above and I will set up your sandbox checkout.</div></div>
<div class="row"><input id="q" placeholder="Ask ABUZ8..." onkeydown="if(event.key==='Enter')send()">
<button onclick="send()">Ask</button></div>
<p class="small">Built by Ahmad Odeh / ABUZ8 LLC for the PayPal AI Hackathon.
Checkout runs on the PayPal Sandbox (no real money moves). The Ask core predates
the hackathon; the PayPal selling flow is the new work — see README.</p>
<script>
const log=document.getElementById('log'),q=document.getElementById('q');
function add(cls,who,text){const d=document.createElement('div');d.className='msg '+cls;
 d.innerHTML='<span class="who"></span><br>';d.querySelector('.who').textContent=who;
 d.appendChild(document.createTextNode(text));log.appendChild(d);log.scrollTop=log.scrollHeight;}
async function send(text){const v=(text||q.value).trim();if(!v)return;q.value='';
 add('user','YOU',v);add('bot','ASK ABUZ8','...thinking...');
 const slot=log.lastChild;
 try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message:v})});const j=await r.json();
  slot.lastChild.textContent=j.reply||('Error: '+(j.error||'unknown'));}
 catch(e){slot.lastChild.textContent='Error: '+e;}}
async function agentCheckout(){
 const out=document.getElementById('buyout');out.textContent=' asking the agent...';
 try{const r=await fetch('/api/agent/checkout',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message:'I want the LotVue360 Dealer Plan.'})});
  const j=await r.json();
  if(j.reply)add('bot','ASK ABUZ8',j.reply);
  if(j.approve_url){out.innerHTML=' checkout ready: ';const a=document.createElement('a');
   a.href=j.approve_url;a.textContent='Approve in PayPal Sandbox';a.style.color='#6cb6ff';out.appendChild(a);}
  else out.textContent=' '+(j.error||'checkout unavailable');}
 catch(e){out.textContent=' Error: '+e;}}
</script></div></body></html>
"""


def result_page(title, body_html):
    return ("<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<title>" + title + "</title><style>"
            "body{background:#0b0f14;color:#e6edf3;font-family:Segoe UI,Arial,sans-serif}"
            ".wrap{max-width:720px;margin:40px auto;padding:0 20px} a{color:#6cb6ff}"
            "</style></head><body><div class=\"wrap\">" + body_html +
            "<p><a href=\"/\">Back to Ask ABUZ8 + PayPal</a></p></div></body></html>")


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        raw = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(length).decode("utf-8")) if length else {}

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        if path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif path == "/health":
            self._send(200, json.dumps({
                "ok": True,
                "model": MODEL,
                "paypal_env": PAYPAL_ENV,
                "paypal_configured": paypal_configured(),
            }))
        elif path == "/paypal/return":
            qs = urllib.parse.parse_qs(parsed.query)
            order_id = (qs.get("token") or [""])[0]
            if not order_id:
                self._send(400, result_page("Missing order", "<h1>No order id returned.</h1>"),
                           "text/html; charset=utf-8")
                return
            try:
                result = capture_paypal_order(order_id)
                status = result.get("status", "UNKNOWN")
                cap_id = ""
                try:
                    cap_id = result["purchase_units"][0]["payments"]["captures"][0]["id"]
                except Exception:
                    pass
                html = ("<h1>Payment captured (Sandbox)</h1>"
                        "<p>Order: " + order_id + "<br>Status: " + status +
                        ("<br>Capture: " + cap_id if cap_id else "") +
                        "</p><p>The agent's sale is complete — verified in the "
                        "PayPal Sandbox, no real money moved.</p>")
                self._send(200, result_page("Payment captured", html), "text/html; charset=utf-8")
            except Exception as e:
                self._send(502, result_page("Capture failed",
                                             "<h1>Capture failed</h1><p>" + type(e).__name__ +
                                             ": " + str(e)[:200] + "</p>"),
                           "text/html; charset=utf-8")
        elif path == "/paypal/cancel":
            self._send(200, result_page("Checkout cancelled",
                                        "<h1>Checkout cancelled</h1><p>No charge was made.</p>"),
                       "text/html; charset=utf-8")
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        try:
            if self.path == "/api/chat":
                body = self._read_json()
                text = (body.get("message") or "").strip()
                if not text:
                    self._send(400, json.dumps({"error": "empty message"}))
                    return
                reply, used_model = chat_completion(text)
                self._send(200, json.dumps({"reply": reply, "model": used_model}))
            elif self.path == "/api/paypal/create-order":
                if not paypal_configured():
                    self._send(503, json.dumps({
                        "error": "PayPal Sandbox is not configured on this host yet "
                                 "(PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET missing)."}))
                    return
                order_id, approve = create_paypal_order("lotvue360-dealer")
                self._send(200, json.dumps({"order_id": order_id, "approve_url": approve}))
            elif self.path == "/api/agent/checkout":
                if not paypal_configured():
                    self._send(503, json.dumps({
                        "error": "PayPal Sandbox is not configured on this host yet "
                                 "(PAYPAL_CLIENT_ID / PAYPAL_CLIENT_SECRET missing)."}))
                    return
                body = self._read_json()
                text = (body.get("message") or "I want the LotVue360 Dealer Plan.").strip()
                reply, _ = chat_completion(
                    "A buyer says: \"" + text + "\" Confirm the LotVue360 Dealer Plan "
                    "offer (USD 99.00/month, first 5 vehicles free) in one short "
                    "paragraph and tell them their PayPal Sandbox checkout is ready.")
                order_id, approve = create_paypal_order("lotvue360-dealer")
                self._send(200, json.dumps({
                    "reply": reply, "order_id": order_id, "approve_url": approve}))
            else:
                self._send(404, json.dumps({"error": "not found"}))
        except urllib.error.HTTPError as e:
            self._send(502, json.dumps({"error": "upstream HTTP " + str(e.code)}))
        except Exception as e:  # surfaced to the caller, never swallowed
            self._send(500, json.dumps({"error": type(e).__name__ + ": " + str(e)[:200]}))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
