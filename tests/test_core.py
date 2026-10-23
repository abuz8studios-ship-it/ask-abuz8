"""
Unit tests for the ISNAD core logic. No third-party deps:

    python3 tests/test_core.py

Every check is a hard assert -- a failure exits non-zero. These tests are
the evidence behind the README's claims about how the verification and
hash-bound approval rules behave.
"""

import copy
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_server"))
import isnad_core as core

ROOT = os.path.join(os.path.dirname(__file__), "..")
SAMPLE = os.path.join(ROOT, "data", "feed.json")

passed = []


def check(name, cond):
    assert cond, f"FAILED: {name}"
    passed.append(name)
    print(f"  ok  {name}")


def fresh_feed() -> core.Feed:
    tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
    with open(SAMPLE, encoding="utf-8") as fh:
        tmp.write(fh.read())
    tmp.close()
    return core.Feed(tmp.name)


print("ISNAD state folding")
feed = fresh_feed()
ms = feed.missions()
check("M-101 folds to VERIFIED (claim + evidence + verification)",
      ms["M-101"]["state"] == core.VERIFIED)
check("M-102 folds to CLAIMED (claim + partial evidence, NO verification)",
      ms["M-102"]["state"] == core.CLAIMED)
check("M-103 folds to VERIFIED", ms["M-103"]["state"] == core.VERIFIED)
check("M-104 folds to IN_PROGRESS", ms["M-104"]["state"] == core.IN_PROGRESS)
check("spoken answer for M-102 never calls it done",
      "NOT verified" in core.say_mission(ms["M-102"]))

print("Unverified claims")
claimed_ids = [ev["mission_id"] for ev in feed.events
               if ev["type"] == "claim" and ev.get("claim") == "done"]
unverified = [m for m in ms.values() if m["state"] == core.CLAIMED]
check("unverified list contains M-102 only",
      [m["mission_id"] for m in unverified] == ["M-102"])

print("Hash-bound approvals")
feed = fresh_feed()
pend = feed.pending_approvals()
check("two approvals pending in sample data", len(pend) == 2)
a201 = [a for a in pend if a["action_id"] == "A-201"][0]
good_hash = a201["payload_hash"]
check("payload hash is a full sha256 hex digest",
      len(good_hash) == 64 and all(c in "0123456789abcdef" for c in good_hash))

tampered = dict(feed.approvals()["A-201"]["payload"], price_usd=4900)
check("tampering the payload changes the hash",
      core.canonical_hash(tampered) != good_hash)

res = feed.decide("A-201", "APPROVED", core.canonical_hash(tampered))
check("deciding with a TAMPERED hash is refused", res["ok"] is False)
check("tampered-hash decision VOIDS the request", res.get("voided") is True)
check("A-201 is no longer pending after the void",
      all(a["action_id"] != "A-201" for a in feed.pending_approvals()))

res = feed.decide("A-201", "APPROVED", good_hash)
check("a voided action cannot be decided afterwards", res["ok"] is False)

feed = fresh_feed()
res = feed.decide("A-202", "DENIED", "deadbeef" * 8)
check("wrong hash is refused even for a DENY", res["ok"] is False)

feed = fresh_feed()
h = feed.approvals()["A-202"]["payload_hash"]
res = feed.decide("A-202", "APPROVED", h)
check("correct hash + APPROVED succeeds", res["ok"] is True)
check("decision got a ledger sequence number", isinstance(res["ledger_seq"], int))

reloaded = core.Feed(feed.path)  # state survives a "new session"
check("decision persists across reload (state across sessions)",
      reloaded.approvals()["A-202"]["status"] == "APPROVED")
res = reloaded.decide("A-202", "DENIED", h)
check("decisions are one-way: second decision refused", res["ok"] is False)

res = reloaded.decide("A-999", "APPROVED", h)
check("unknown action id refused", res["ok"] is False)

print(f"\nALL {len(passed)} CHECKS PASSED")
