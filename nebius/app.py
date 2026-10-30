#!/usr/bin/env python3
"""Ask ABUZ8 on Nebius — Nebius x NVIDIA Hackathon entry.

One core (Ask ABUZ8) answering live through Nebius Token Factory with
NVIDIA Nemotron-3-Nano-30B-A3B. Stdlib-only server: no dependencies.

Credential: NEBIUS_API_KEY env var when deployed. For local development
inside the Muse VM, falls back to the custom-connector surrogate helper.
"""
import json
import os
import sys
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BASE_URL = "https://api.tokenfactory.nebius.com/v1/"
MODEL = "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B"  # verified live 2026-10-30 via /v1/models
PORT = int(os.environ.get("PORT", "8899"))

SYSTEM_PROMPT = (
    "You are Ask ABUZ8, the front door of ABUZ8 LLC — a one-person AI company run "
    "by a fleet of autonomous agents (Aisha, Asred, Aida, Qadir, Zait, Amanecer). "
    "Your rule is ISNAD: a claim is not a fact. You separate what is CLAIMED from "
    "what is VERIFIED, you never upgrade a claim into a fact, and money-out, "
    "publishing, and irreversible actions always wait for the owner's approval. "
    "Answer concisely, concretely, and honestly. If you do not know, say so."
)

PAGE = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Ask ABUZ8 — on Nebius Token Factory (NVIDIA Nemotron)</title>
<style>
 body{background:#0b0f14;color:#e6edf3;font-family:Segoe UI,Arial,sans-serif;margin:0}
 .wrap{max-width:820px;margin:0 auto;padding:28px 20px 40px}
 h1{font-size:30px;margin:0 0 4px} .sub{color:#9fb0c3;margin:0 0 6px}
 .badge{display:inline-block;background:#12351f;color:#3fb96b;border:1px solid #3fb96b;border-radius:20px;padding:1px 10px;font-size:12px;font-weight:700}
 #log{background:#11161d;border:1px solid #26313f;border-radius:10px;padding:16px;min-height:280px;margin:18px 0}
 .msg{margin:10px 0;line-height:1.5} .who{font-weight:700;font-size:12px;letter-spacing:.6px}
 .user .who{color:#6cb6ff} .bot .who{color:#ffb454}
 .row{display:flex;gap:8px} input{flex:1;background:#11161d;border:1px solid #26313f;border-radius:8px;color:#e6edf3;padding:11px 12px;font-size:15px}
 button{background:#1f6feb;border:0;color:#fff;border-radius:8px;padding:11px 18px;font-size:15px;cursor:pointer}
 .chips{margin:10px 0} .chip{background:#1a222d;border:1px solid #26313f;color:#c9d6e3;border-radius:16px;padding:4px 12px;margin:2px;cursor:pointer;font-size:13px}
 .small{color:#9fb0c3;font-size:13px;margin-top:14px}
</style></head><body><div class="wrap">
<h1>Ask ABUZ8</h1>
<p class="sub">The front door of a one-person AI company — now answering on
<b>Nebius Token Factory</b> with <b>NVIDIA Nemotron-3-Nano-30B-A3B</b>.</p>
<span class="badge">LIVE MODEL: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B</span>
<div class="chips">
 <button class="chip" onclick="ask(this)">What is Ask ABUZ8's job for a car dealership?</button>
 <button class="chip" onclick="ask(this)">What does CLAIMED vs VERIFIED mean in your fleet?</button>
 <button class="chip" onclick="ask(this)">Which actions always wait for the owner's approval?</button>
</div>
<div id="log"><div class="msg bot"><span class="who">ASK ABUZ8</span><br>Ask me anything about the fleet, the company, or how I keep agent claims honest. Every answer below is generated live by Nemotron on Token Factory.</div></div>
<div class="row"><input id="q" placeholder="Ask ABUZ8..." onkeydown="if(event.key==='Enter')send()">
<button onclick="send()">Ask</button></div>
<p class="small">Built by Ahmad Odeh / ABUZ8 LLC for the Nebius × NVIDIA Global AI Hackathon (Best Apps and Agents).
Core app predates the hackathon; the Token Factory wiring is the in-window update — see README.</p>
<script>
const log=document.getElementById('log'),q=document.getElementById('q');
function add(cls,who,text){const d=document.createElement('div');d.className='msg '+cls;
 d.innerHTML='<span class="who"></span><br>';d.querySelector('.who').textContent=who;
 d.appendChild(document.createTextNode(text));log.appendChild(d);log.scrollTop=log.scrollHeight;}
async function send(text){const v=(text||q.value).trim();if(!v)return;q.value='';
 add('user','YOU',v);add('bot','ASK ABUZ8','...thinking on Nemotron...');
 const slot=log.lastChild;
 try{const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({message:v})});const j=await r.json();
  slot.lastChild.textContent=j.reply||('Error: '+(j.error||'unknown'));}
 catch(e){slot.lastChild.textContent='Error: '+e;}}
function ask(b){send(b.textContent);}
</script></div></body></html>
"""


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


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        raw = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif self.path == "/health":
            self._send(200, json.dumps({"ok": True, "model": MODEL}))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, json.dumps({"error": "not found"}))
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            text = (body.get("message") or "").strip()
            if not text:
                self._send(400, json.dumps({"error": "empty message"}))
                return
            reply, used_model = chat_completion(text)
            self._send(200, json.dumps({"reply": reply, "model": used_model}))
        except urllib.error.HTTPError as e:
            self._send(502, json.dumps({"error": "upstream HTTP " + str(e.code)}))
        except Exception as e:  # surfaced to the caller, never swallowed
            self._send(500, json.dumps({"error": type(e).__name__ + ": " + str(e)[:200]}))

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
