"""
End-to-end smoke test: boots the real MCP server over Streamable HTTP and
talks to it with raw JSON-RPC -- the same protocol Alexa+ speaks.

    .venv/bin/python tests/smoke_mcp.py

Verifies: initialize handshake negotiates MCP protocol 2025-11-25,
tools/list exposes the five concierge tools, and a full conversation works
(status -> unverified claims -> approvals -> hash-bound approve -> the
decision is visible in a fresh call), and that the Host allowlist accepts the
public name while refusing unknown hosts with 421. Exits non-zero on any
failure.
"""

import http.client
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
PORT = 8399
BASE = f"http://127.0.0.1:{PORT}"
_id = 0


def rpc(method, params=None, session=None):
    global _id
    _id += 1
    body = {"jsonrpc": "2.0", "id": _id, "method": method}
    if params is not None:
        body["params"] = params
    headers = {"Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    req = urllib.request.Request(BASE + "/mcp", data=json.dumps(body).encode(),
                                 headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read().decode()
        sid = resp.headers.get("mcp-session-id")
    if raw.lstrip().startswith("event:") or "\ndata:" in raw:
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:]), sid
        raise AssertionError("SSE response carried no data line")
    return json.loads(raw), sid


def raw_post_status(host_header):
    """POST /mcp with a forged Host header (what a proxy/tunnel sends)."""
    conn = http.client.HTTPConnection("127.0.0.1", PORT, timeout=15)
    body = json.dumps({"jsonrpc": "2.0", "id": 999, "method": "tools/list",
                       "params": {}})
    conn.request("POST", "/mcp", body=body,
                 headers={"Content-Type": "application/json",
                          "Accept": "application/json, text/event-stream",
                          "Host": host_header})
    status = conn.getresponse().status
    conn.close()
    return status


def call(name, args=None):
    out, _ = rpc("tools/call", {"name": name, "arguments": args or {}})
    assert "result" in out, f"{name} errored: {out}"
    text = "".join(c.get("text", "") for c in out["result"]["content"])
    return json.loads(text)


def main():
    tmp = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    with open(os.path.join(ROOT, "data", "feed.json"), "rb") as fh:
        tmp.write(fh.read())
    tmp.close()

    env = dict(os.environ, ASK_ABUZ8_FEED=tmp.name, PORT=str(PORT),
                     ASK_ABUZ8_ALLOWED_HOSTS="public.example")
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "mcp_server", "server.py")],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for _ in range(60):
            try:
                with urllib.request.urlopen(BASE + "/health", timeout=2) as r:
                    if r.status == 200:
                        break
            except Exception:
                time.sleep(0.5)
        else:
            raise AssertionError("server did not come up:\n" +
                                 (proc.stdout.read() if proc.stdout else ""))

        init, session = rpc("initialize", {
            "protocolVersion": "2025-11-25",
            "capabilities": {},
            "clientInfo": {"name": "smoke-test", "version": "1.0"},
        })
        proto = init["result"]["protocolVersion"]
        print(f"  ok  initialize -> protocolVersion {proto}")
        assert proto == "2025-11-25", f"negotiated {proto}, need 2025-11-25"

        tools, _ = rpc("tools/list", {}, session)
        names = sorted(t["name"] for t in tools["result"]["tools"])
        print(f"  ok  tools/list -> {names}")
        assert names == ["company_status", "decide_approval", "mission_status",
                         "pending_approvals", "unverified_claims"], names

        assert raw_post_status("public.example") == 200
        print("  ok  Host: public.example (allowlisted) -> 200 on /mcp")
        assert raw_post_status("evil.example") == 421
        print("  ok  Host: evil.example (not allowlisted) -> 421 refused")

        st = call("company_status")
        print(f"  ok  company_status -> {st['by_state']}, pending {st['pending_approvals']}")
        assert st["by_state"].get("VERIFIED") == 2 and st["pending_approvals"] == 2

        uc = call("unverified_claims")
        assert [m["mission_id"] for m in uc["missions"]] == ["M-102"], uc
        print(f"  ok  unverified_claims -> only M-102 (CLAIMED != DONE holds over MCP)")

        pa = call("pending_approvals")
        a201 = [a for a in pa["approvals"] if a["action_id"] == "A-201"][0]
        print(f"  ok  pending_approvals -> A-201 short hash {a201['short_hash']}")

        bad = call("decide_approval", {"action_id": "A-201", "decision": "APPROVED",
                                       "payload_hash": "0" * 64})
        assert bad["ok"] is False and bad.get("voided") is True, bad
        print("  ok  decide_approval with wrong hash -> refused + VOIDED")

        pa2 = call("pending_approvals")
        a202 = [a for a in pa2["approvals"] if a["action_id"] == "A-202"][0]
        ok = call("decide_approval", {"action_id": "A-202", "decision": "APPROVED",
                                      "payload_hash": a202["payload_hash"]})
        assert ok["ok"] is True, ok
        print(f"  ok  decide_approval with correct hash -> APPROVED, ledger seq {ok['ledger_seq']}")

        pa3 = call("pending_approvals")
        assert pa3["count"] == 0, pa3
        print("  ok  pending_approvals after decisions -> 0 (state persists across calls)")

        print("\nSMOKE TEST PASSED: MCP 2025-11-25 over Streamable HTTP, end to end.")
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
