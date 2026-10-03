"""App-level enforcement of the SAME policy file OpenShell uses (subset: filesystem_policy + network_policies).
Purpose: (1) fallback if OpenShell can't run on a dev machine, (2) defence in depth, (3) gives the UI
an audit entry for every decision. Not a replacement for kernel/proxy enforcement.
Known simplifications vs OpenShell: `binaries` are ignored; path globs use fnmatch; no TLS inspection."""
import fnmatch, os
from pathlib import Path
from urllib.parse import urlparse
import yaml
from . import config


class PolicyDenied(Exception):
    def __init__(self, layer, reason):
        super().__init__(reason)
        self.layer, self.reason = layer, reason


def _os_policy():
    raw = config.POLICY_TEMPLATE.read_text().replace("__NOGAIN_HOME__", str(config.HOME))
    return yaml.safe_load(raw)


def _app_policy():
    return yaml.safe_load(config.APP_POLICY.read_text())


def tool_spec(name):
    return _app_policy().get("tools", {}).get(name)


def taint_rule_on():
    return bool(_app_policy().get("untrusted_content", {}).get("block_risky_tools_when_tainted", True))


def resolve_path(p: str) -> Path:
    p = os.path.expanduser(p)
    if not os.path.isabs(p):
        p = os.path.join(config.HOME, p)
    return Path(os.path.realpath(p))


def check_fs(path: str, mode: str = "r") -> Path:
    fs = _os_policy().get("filesystem_policy", {})
    rw = [Path(os.path.realpath(x)) for x in fs.get("read_write", [])]
    ro = [Path(os.path.realpath(x)) for x in fs.get("read_only", [])]
    roots = rw + (ro if mode == "r" else [])
    p = resolve_path(path)
    if any(p == r or r in p.parents for r in roots):
        return p
    raise PolicyDenied("filesystem", f"{p} is outside approved folders ({mode})")


_PRESETS = {
    "read-only": {"GET", "HEAD", "OPTIONS"},
    "read-write": {"GET", "HEAD", "OPTIONS", "POST", "PUT", "PATCH"},
}


def check_net(method: str, url: str):
    u = urlparse(url)
    host = (u.hostname or "").lower()
    port = u.port or (443 if u.scheme == "https" else 80)
    for rule in (_os_policy().get("network_policies") or {}).values():
        for ep in rule.get("endpoints", []):
            ports = ep.get("ports") or [ep.get("port")]
            if not fnmatch.fnmatch(host, str(ep.get("host", "")).lower()) or port not in ports:
                continue
            if "access" in ep:
                if ep["access"] == "full" or method.upper() in _PRESETS.get(ep["access"], set()):
                    return
            elif "rules" in ep:
                for r in ep["rules"]:
                    a = r.get("allow", {})
                    if a.get("method", "*") in ("*", method.upper()) and fnmatch.fnmatch(
                        u.path or "/", a.get("path", "**").replace("**", "*")
                    ):
                        return
            else:
                return
    raise PolicyDenied("network", f"{method.upper()} {host}:{port}{u.path} not in network allowlist")
