"""Append-only audit log shown in the UI. Every tool call and every LLM call lands here."""
import json, time
from . import store


def log(actor, tool, target, decision, layer, detail=None):
    store.execute(
        "INSERT INTO audit(ts,actor,tool,target,decision,layer,detail) VALUES(?,?,?,?,?,?,?)",
        (time.time(), actor, tool, str(target)[:300], decision, layer, json.dumps(detail or {})[:1000]),
    )


def recent(limit=100):
    return store.query("SELECT * FROM audit ORDER BY id DESC LIMIT ?", (limit,))
