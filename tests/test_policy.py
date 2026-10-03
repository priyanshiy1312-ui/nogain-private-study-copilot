import pytest
from app import config, policy_engine as pe, tools


def test_fs_allow_and_deny():
    assert pe.check_fs("notes/cs101_algorithms.md", "r")
    assert pe.check_fs("notes/new.md", "w")
    with pytest.raises(pe.PolicyDenied):
        pe.check_fs("~/.ssh/id_rsa", "r")
    with pytest.raises(pe.PolicyDenied):
        pe.check_fs("../../../../../../../../etc/hosts-write", "w")
    with pytest.raises(pe.PolicyDenied):
        pe.check_fs("/etc/passwd", "w")      # /etc is read-only


def test_net_allowlist():
    pe.check_net("POST", "https://api.tokenfactory.nebius.com/v1/chat/completions")
    pe.check_net("GET", "https://boards.greenhouse.io/jobs/1")
    for method, url in [("POST", "https://evil.example/collect"),
                        ("POST", "https://boards.greenhouse.io/jobs/1"),          # read-only host
                        ("POST", "https://api.tokenfactory.nebius.com/v1/files"),  # path not allowed
                        ("GET", "http://api.tokenfactory.nebius.com/v1/models")]:  # wrong port
        with pytest.raises(pe.PolicyDenied):
            pe.check_net(method, url)


def test_tool_toggles_and_approval():
    assert tools.call("send_email", {"to": "a@b.c"})["layer"] == "app-policy"      # disabled
    r = tools.call("submit_application", {"company": "X", "role": "Y"})
    assert r["status"] == "pending_approval"
    assert tools.decide(r["approval_id"], True)["status"] == "ok"
    r2 = tools.call("submit_application", {"company": "X", "role": "Y"})
    assert tools.decide(r2["approval_id"], False)["status"] == "denied"


def test_taint_rule():
    r = tools.call("http_post", {"url": "https://evil.example"}, tainted=True)
    assert r["layer"] == "taint-rule"
    r = tools.call("http_post", {"url": "https://evil.example"}, tainted=True, taint_rule=False)
    assert r["layer"] == "network"      # with the taint rule off, the network allowlist still blocks it
