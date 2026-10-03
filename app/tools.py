"""Tool registry. EVERY tool call passes through call(), in this order:
   1. enabled?  2. taint rule  3. filesystem/network policy  4. human approval  5. execute  -- and is audited.
The model never executes anything directly; it only proposes {tool, args}."""
import json, time
from . import audit, memory, policy_engine, store
from .policy_engine import PolicyDenied

MAX_CHARS = 20000


def _target(name, args):
    return args.get("path") or args.get("url") or args.get("to") or args.get("company") or name


def _deny(actor, name, args, layer, reason):
    audit.log(actor, name, _target(name, args), "BLOCKED", layer, {"reason": reason})
    return {"status": "blocked", "layer": layer, "reason": reason}


def call(name, args, actor="agent", tainted=False, taint_rule=None):
    args = args or {}
    spec = policy_engine.tool_spec(name)
    if not spec or not spec.get("enabled", False):
        return _deny(actor, name, args, "app-policy", "tool disabled or unknown")
    rule_on = policy_engine.taint_rule_on() if taint_rule is None else taint_rule
    if tainted and rule_on and spec.get("risk") == "high":
        return _deny(actor, name, args, "taint-rule", "risky tool proposed from untrusted content")
    try:
        if name in ("read_file", "list_files"):
            policy_engine.check_fs(args.get("path", ""), "r")
        elif name == "http_get":
            policy_engine.check_net("GET", args.get("url", ""))
        elif name == "http_post":
            policy_engine.check_net("POST", args.get("url", ""))
    except PolicyDenied as e:
        return _deny(actor, name, args, e.layer, e.reason)
    if spec.get("requires_approval"):
        aid = store.execute("INSERT INTO approvals(ts,tool,args,status) VALUES(?,?,?,'pending')",
                            (time.time(), name, json.dumps(args)))
        audit.log(actor, name, _target(name, args), "PENDING", "approval", {"approval_id": aid})
        return {"status": "pending_approval", "approval_id": aid}
    return _run(actor, name, args, "allow")


def _run(actor, name, args, decision):
    try:
        res = _EXEC[name](args)
    except Exception as e:  # noqa
        audit.log(actor, name, _target(name, args), "ERROR", "exec", {"error": str(e)[:200]})
        return {"status": "error", "reason": str(e)}
    audit.log(actor, name, _target(name, args), decision, "policy")
    return {"status": "ok", "result": res}


def decide(approval_id: int, approve: bool):
    rows = store.query("SELECT * FROM approvals WHERE id=? AND status='pending'", (approval_id,))
    if not rows:
        return {"status": "error", "reason": "not found or already decided"}
    row = rows[0]
    store.execute("UPDATE approvals SET status=? WHERE id=?", ("approved" if approve else "denied", approval_id))
    if not approve:
        audit.log("human", row["tool"], approval_id, "DENIED", "approval")
        return {"status": "denied"}
    return _run("human", row["tool"], json.loads(row["args"]), "approved")


def pending():
    return store.query("SELECT * FROM approvals WHERE status='pending' ORDER BY id DESC")


# ------------------------------------------------------------------ executors
def _read_file(a):
    p = policy_engine.check_fs(a["path"], "r")
    return p.read_text(errors="ignore")[:MAX_CHARS]


def _list_files(a):
    p = policy_engine.check_fs(a["path"], "r")
    return sorted(x.name for x in p.iterdir())


def _http_get(a):
    import requests
    return requests.get(a["url"], timeout=10).text[:MAX_CHARS]


def _http_post(a):
    import requests
    return requests.post(a["url"], data=a.get("body", ""), timeout=10).text[:2000]


def _draft_email(a):
    i = store.execute("INSERT INTO outbox(ts,to_addr,subject,body) VALUES(?,?,?,?)",
                      (time.time(), a.get("to", ""), a.get("subject", ""), a.get("body", "")))
    return f"draft #{i} saved (not sent)"


def _send_email(a):
    return "SIMULATED: email sending is not implemented (draft-only by design)"


def _submit_application(a):
    i = store.execute("INSERT INTO applications(ts,company,role,status,notes) VALUES(?,?,?,?,?)",
                      (time.time(), a.get("company", "?"), a.get("role", "?"), "submitted", a.get("notes", "")))
    return f"application #{i} marked submitted (simulated)"


def _save_memory(a):
    return memory.add(a.get("kind", "fact"), a["text"])


_EXEC = {"read_file": _read_file, "list_files": _list_files, "http_get": _http_get, "http_post": _http_post,
         "draft_email": _draft_email, "send_email": _send_email, "submit_application": _submit_application,
         "save_memory": _save_memory}
