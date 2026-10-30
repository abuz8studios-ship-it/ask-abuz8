"""
Ask ABUZ8 -- a self-hosted MCP server (Model Context Protocol spec
2025-11-25, Streamable HTTP) that acts as the voice concierge's brain for
the ABUZ8 agent company, plus the simulated Alexa+ web experience that
talks to it.

Alexa+ integration path (per the Build, Ship, Shape rules): a working
self-hosted MCP server implementing MCP spec 2025-11-25 over Streamable
HTTP, plus the optional simulated Alexa+ experience in a web app.

What the tools do -- all real, no mocks:
  company_status     ISNAD roll-up: missions by VERIFIED state, approvals
  mission_status     one mission (or all): claimed vs verified, evidence
  unverified_claims  missions an agent CLAIMS are done but nobody verified
  pending_approvals  Tier-3 (send / spend / publish) actions awaiting the
                     owner, each with the short hash of its exact payload
  decide_approval    the owner's decision -- HASH-BOUND: the decision only
                     applies if the payload hash presented with it matches
                     the payload that was originally presented. A changed
                     payload voids the approval. Decisions are appended to
                     the append-only ledger and persist across sessions.

Run:
  pip install -r requirements.txt
  python mcp_server/server.py            # http://127.0.0.1:8377/mcp
  open http://127.0.0.1:8377/            # the simulated Alexa+ experience

Env:
  ASK_ABUZ8_FEED   path to the feed JSON (default: data/feed.runtime.json,
                   auto-seeded from data/feed.json on first run)
  PORT             default 8377
  ASK_ABUZ8_ALLOWED_HOSTS  comma-separated public hostnames accepted on /mcp
                   behind a proxy/tunnel (required for public exposure --
                   without it the SDK answers proxied calls with 421)
"""

import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse

import isnad_core as core

if getattr(sys, "frozen", False):  # PyInstaller appliance: data sits next to the exe
    ROOT = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIM_DIR = os.path.join(ROOT, "simulator")

# ------------------------------------------------------------------- feed ---

def feed_path() -> str:
    env = os.environ.get("ASK_ABUZ8_FEED")
    if env:
        return env
    runtime = os.path.join(ROOT, "data", "feed.runtime.json")
    if not os.path.exists(runtime):
        shutil.copyfile(os.path.join(ROOT, "data", "feed.json"), runtime)
    return runtime


def transport_security():
    """DNS-rebinding allowlist: localhost always, plus ASK_ABUZ8_ALLOWED_HOSTS.

    The SDK locks loopback binds to localhost Host headers only, so a reverse
    proxy or tunnel that forwards the public Host gets a 421 on /mcp unless
    the public name is allowlisted. Comma-separated; bare hosts or full URLs.
    Unset -> SDK default behavior (strict localhost on loopback binds).
    """
    extra = [h.strip() for h in os.environ.get("ASK_ABUZ8_ALLOWED_HOSTS", "").split(",") if h.strip()]
    if not extra:
        return None
    hosts = ["127.0.0.1:*", "localhost:*", "[::1]:*"]
    origins = ["http://127.0.0.1:*", "http://localhost:*", "http://[::1]:*"]
    for h in extra:
        h = h.split("://", 1)[-1].rstrip("/")
        hosts += [h, h + ":*"]
        origins += ["https://" + h, "http://" + h]
    return TransportSecuritySettings(enable_dns_rebinding_protection=True,
                                     allowed_hosts=hosts, allowed_origins=origins)


def load_feed() -> core.Feed:
    """Fresh read on every call: the file is the shared state, so decisions
    persist across sessions and are visible to every front-end."""
    return core.Feed(feed_path())


def _mission_view(m: dict) -> dict:
    return {
        "mission_id": m["mission_id"],
        "title": m["title"],
        "agent": m["agent"],
        "state": m["state"],
        "evidence_count": len(m["evidence"]),
        "say": core.say_mission(m),
    }


# ----------------------------------------------------------------- server ---

mcp = FastMCP(
    "ask-abuz8",
    instructions=(
        "Ask ABUZ8 is the concierge for an autonomous agent company. It "
        "reports mission status using ISNAD verification: an agent's claim "
        "is never reported as fact. States are OPEN, IN_PROGRESS, CLAIMED "
        "(claimed, NOT verified), VERIFIED, DISPUTED. Tier-3 actions "
        "(sending, spending, publishing) require the owner's approval, "
        "bound to the exact payload by its SHA-256 hash."
    ),
    transport_security=transport_security(),
    host=os.environ.get("FASTMCP_HOST", "127.0.0.1"),
    stateless_http=True,
    json_response=True,
    port=int(os.environ.get("PORT", "8377")),
)


@mcp.tool()
def company_status() -> dict:
    """Roll-up of the whole company: missions by ISNAD state + approvals."""
    feed = load_feed()
    ms = feed.missions()
    counts = {}
    for m in ms.values():
        counts[m["state"]] = counts.get(m["state"], 0) + 1
    return {
        "company": feed.doc.get("company", "ABUZ8"),
        "missions_total": len(ms),
        "by_state": counts,
        "pending_approvals": len(feed.pending_approvals()),
        "say": core.say_status(feed),
    }


@mcp.tool()
def mission_status(mission_id: str = "") -> dict:
    """Status of one mission by id (e.g. 'M-101'), or all missions.

    The answer separates what the agent CLAIMED from what is VERIFIED --
    the core ISNAD rule. A CLAIMED mission is never reported as done.
    """
    feed = load_feed()
    ms = feed.missions()
    if mission_id:
        m = ms.get(mission_id.strip().upper())
        if m is None:
            return {"error": f"no mission {mission_id!r} on the board",
                    "say": f"I don't see a mission {mission_id} on the board."}
        view = _mission_view(m)
        view["evidence"] = [e.get("evidence") for e in m["evidence"]]
        return view
    views = [_mission_view(m) for m in ms.values()]
    return {"missions": views,
            "say": " ".join(v["say"] for v in views)}


@mcp.tool()
def unverified_claims() -> dict:
    """Missions an agent claims are done that are NOT yet verified.

    This is the question no ordinary status bot can answer honestly:
    'what is still only claimed?'"""
    feed = load_feed()
    claimed = [m for m in feed.missions().values() if m["state"] == core.CLAIMED]
    views = [_mission_view(m) for m in claimed]
    say = ("Nothing is sitting at claimed-but-unverified right now."
           if not views else
           f"{len(views)} mission(s) are claimed but NOT verified: " +
           " ".join(v["say"] for v in views))
    return {"count": len(views), "missions": views, "say": say}


@mcp.tool()
def pending_approvals() -> dict:
    """Tier-3 actions waiting for the owner's decision.

    Each action is presented with the short hash (first 8 hex chars of the
    SHA-256) of its exact payload. The owner repeats that hash when
    deciding, which binds the decision to the exact payload presented.
    """
    feed = load_feed()
    pend = feed.pending_approvals()
    views = [{
        "action_id": a["action_id"],
        "action": a["action"],
        "tier": a["tier"],
        "requested_by": a["requested_by"],
        "payload": a["payload"],
        "payload_hash": a["payload_hash"],
        "short_hash": a["payload_hash"][:8],
        "say": (f"{a['action_id']}: {a['action']} "
                f"Requested by {a['requested_by']}. "
                f"Payload hash {a['payload_hash'][:8]}."),
    } for a in pend]
    say = ("No Tier-3 actions are waiting for your decision."
           if not views else
           f"{len(views)} action(s) need your decision: " +
           " ".join(v["say"] for v in views))
    return {"count": len(views), "approvals": views, "say": say}


@mcp.tool()
def decide_approval(action_id: str, decision: str, payload_hash: str) -> dict:
    """Record the owner's decision on a Tier-3 action. HASH-BOUND.

    decision: "APPROVED" or "DENIED".
    payload_hash: the full SHA-256 the owner was presented for this exact
    payload (the pending_approvals tool returns it; the simulator shows
    the short form for comparison). If the payload changed after the
    request, the hash will not match and the approval is VOIDED -- the
    decision is never applied to a payload the owner did not see.
    The decision is appended to the ledger and is one-way.
    """
    feed = load_feed()
    result = feed.decide(action_id.strip().upper(), decision.strip().upper(),
                         payload_hash.strip(), by="owner-via-alexaplus")
    if result.get("ok"):
        result["say"] = (f"{result['decision']}: {action_id} is recorded in the "
                         f"ledger as entry {result['ledger_seq']}. It cannot be undone.")
    else:
        result["say"] = result.get("error", "The decision was refused.")
    return result


# ------------------------------------------------------- simulator host ---

@mcp.custom_route("/", methods=["GET"])
async def simulator_page(request: Request) -> HTMLResponse:
    with open(os.path.join(SIM_DIR, "index.html"), "r", encoding="utf-8") as fh:
        return HTMLResponse(fh.read())


@mcp.custom_route("/intents.json", methods=["GET"])
async def intents_json(request: Request) -> JSONResponse:
    with open(os.path.join(SIM_DIR, "intents.json"), "r", encoding="utf-8") as fh:
        return JSONResponse(json.load(fh))


@mcp.custom_route("/health", methods=["GET"])
async def health(request: Request) -> PlainTextResponse:
    return PlainTextResponse("ask-abuz8 mcp server: ok")


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
