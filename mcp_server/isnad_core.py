"""
ISNAD core logic for Ask ABUZ8.

ISNAD is the verification discipline used by the ABUZ8 agent company:
a claim is not a fact. An agent SAYING a mission is done puts the mission in
the CLAIMED state. Only a separate verification event, backed by evidence
recorded in the append-only feed, moves it to VERIFIED.

CLAIMED != DONE. This module is the single source of truth for that rule.
It is pure logic (no MCP dependency) so it can be unit-tested directly and
reused by any front-end: the MCP server in this repo, the web simulator,
or the production company harness on Pegasus.

Feed format: a JSON document {"company": ..., "events": [ ... ]} where the
events list is append-only. Relevant event types:

  mission_created   {mission_id, title, agent, tier}
  claim             {mission_id, agent, claim: "done"|"progress", detail}
  evidence          {mission_id, evidence, by}
  verification      {mission_id, verdict: "VERIFIED"|"DISPUTED", by}
  approval_requested{action_id, tier, action, payload, requested_by}
  approval_decided  {action_id, decision: "APPROVED"|"DENIED"|"VOID",
                     by, payload_hash}
"""

import hashlib
import json
import os
import tempfile

# ---------------------------------------------------------------- states ---

OPEN = "OPEN"                # created, no claim yet
IN_PROGRESS = "IN_PROGRESS"  # agent reported progress, not done
CLAIMED = "CLAIMED"          # agent claims done -- NOT verified
VERIFIED = "VERIFIED"        # independently verified against evidence
DISPUTED = "DISPUTED"        # verification failed / claim rejected


def canonical_hash(payload) -> str:
    """SHA-256 of the canonical JSON encoding of a payload.

    The hash is what binds a human approval to the EXACT action that was
    presented. If the payload changes after the request, the hash changes
    and the approval no longer matches -- the decision is refused.
    """
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def short_hash(payload) -> str:
    """First 8 hex chars -- the form a human can compare by eye / by voice."""
    return canonical_hash(payload)[:8]


# ------------------------------------------------------------------ feed ---

class Feed:
    """An append-only event feed backed by a JSON file."""

    def __init__(self, path: str):
        self.path = path
        with open(path, "r", encoding="utf-8") as fh:
            self.doc = json.load(fh)
        self.events = self.doc.setdefault("events", [])

    # -- persistence -------------------------------------------------------
    def append(self, event: dict) -> dict:
        """Append an event and persist atomically. Append-only: events are
        never edited or removed, so the ledger is the permanent record."""
        event = dict(event)
        event["seq"] = (self.events[-1]["seq"] + 1) if self.events else 1
        self.events.append(event)
        directory = os.path.dirname(os.path.abspath(self.path))
        fd, tmp = tempfile.mkstemp(dir=directory, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(self.doc, fh, indent=2)
            os.replace(tmp, self.path)
        except BaseException:
            if os.path.exists(tmp):
                os.remove(tmp)
            raise
        return event

    # -- missions ----------------------------------------------------------
    def missions(self) -> dict:
        """Fold the event log into per-mission ISNAD state."""
        out = {}
        for ev in self.events:
            mid = ev.get("mission_id")
            if not mid:
                continue
            m = out.setdefault(mid, {
                "mission_id": mid, "title": None, "agent": None, "tier": None,
                "state": OPEN, "claims": [], "evidence": [], "verdicts": [],
            })
            t = ev["type"]
            if t == "mission_created":
                m["title"] = ev.get("title")
                m["agent"] = ev.get("agent")
                m["tier"] = ev.get("tier")
            elif t == "claim":
                m["claims"].append(ev)
                if ev.get("claim") == "done" and m["state"] in (OPEN, IN_PROGRESS):
                    m["state"] = CLAIMED
                elif ev.get("claim") == "progress" and m["state"] == OPEN:
                    m["state"] = IN_PROGRESS
            elif t == "evidence":
                m["evidence"].append(ev)
            elif t == "verification":
                m["verdicts"].append(ev)
                m["state"] = VERIFIED if ev.get("verdict") == "VERIFIED" else DISPUTED
        return out

    def mission(self, mission_id: str):
        return self.missions().get(mission_id)

    # -- approvals ---------------------------------------------------------
    def approvals(self) -> dict:
        """Fold the event log into per-action approval state."""
        out = {}
        for ev in self.events:
            aid = ev.get("action_id")
            if not aid:
                continue
            if ev["type"] == "approval_requested":
                out[aid] = {
                    "action_id": aid,
                    "tier": ev.get("tier"),
                    "action": ev.get("action"),
                    "payload": ev.get("payload"),
                    "requested_by": ev.get("requested_by"),
                    "payload_hash": canonical_hash(ev.get("payload")),
                    "status": "PENDING",
                    "decision": None,
                }
            elif ev["type"] == "approval_decided" and aid in out:
                out[aid]["status"] = ev.get("decision")
                out[aid]["decision"] = ev
        return out

    def pending_approvals(self) -> list:
        return [a for a in self.approvals().values() if a["status"] == "PENDING"]

    def decide(self, action_id: str, decision: str, presented_hash: str,
               by: str = "owner") -> dict:
        """Record a human decision on a Tier-3 action -- hash-bound.

        Rules (enforced here, in code, not in a prompt):
        * the action must exist and still be PENDING (one-way lifecycle);
        * the presented payload hash must equal the hash of the payload that
          was presented when the action was requested. If the payload was
          edited after the request, the hashes differ and the decision is
          refused and the request is VOIDED;
        * the decision is appended to the ledger permanently.
        """
        if decision not in ("APPROVED", "DENIED"):
            return {"ok": False, "error": f"decision must be APPROVED or DENIED, got {decision!r}"}
        approvals = self.approvals()
        ap = approvals.get(action_id)
        if ap is None:
            return {"ok": False, "error": f"unknown action_id {action_id!r}"}
        if ap["status"] != "PENDING":
            return {"ok": False, "error": f"{action_id} is already {ap['status']} -- decisions are one-way"}
        if presented_hash.lower() != ap["payload_hash"]:
            self.append({
                "type": "approval_decided", "action_id": action_id,
                "decision": "VOID", "by": by,
                "payload_hash": ap["payload_hash"],
                "note": "presented hash did not match requested payload -- approval voided",
            })
            return {"ok": False, "voided": True,
                    "error": "payload hash mismatch -- the action changed after it was "
                             "presented, so the approval was VOIDED, not applied"}
        ev = self.append({
            "type": "approval_decided", "action_id": action_id,
            "decision": decision, "by": by,
            "payload_hash": ap["payload_hash"],
        })
        return {"ok": True, "action_id": action_id, "decision": decision,
                "ledger_seq": ev["seq"], "payload_hash": ap["payload_hash"]}


# ------------------------------------------------------- voice formatting ---

def say_mission(m: dict) -> str:
    """One spoken-style sentence about a mission. Never upgrades a claim."""
    if m["state"] == VERIFIED:
        return (f"{m['title']}: verified done. "
                f"{len(m['evidence'])} evidence item(s) on record.")
    if m["state"] == CLAIMED:
        return (f"{m['title']}: {m['agent']} claims it is done, but it is NOT verified yet. "
                f"Claimed is not done.")
    if m["state"] == DISPUTED:
        return f"{m['title']}: disputed. The claim did not survive verification."
    if m["state"] == IN_PROGRESS:
        return f"{m['title']}: in progress by {m['agent']}."
    return f"{m['title']}: open, no claim yet."


def say_status(feed: Feed) -> str:
    ms = feed.missions()
    counts = {}
    for m in ms.values():
        counts[m["state"]] = counts.get(m["state"], 0) + 1
    pend = len(feed.pending_approvals())
    parts = [f"{len(ms)} missions on the board."]
    for st in (VERIFIED, CLAIMED, IN_PROGRESS, DISPUTED, OPEN):
        if counts.get(st):
            parts.append(f"{counts[st]} {st.lower()}.")
    parts.append(f"{pend} approval(s) waiting for you." if pend else "No approvals waiting.")
    return " ".join(parts)
