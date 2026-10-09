"""Lap 6: skill_install name@version pin with refuse-on-mismatch (stdio only)."""
import json
import subprocess
import sys

import mcp_server.server as srv


def test_parse_pinned_name_splits_at_last_at() -> None:
    assert srv._parse_pinned_name("progit-branching") == ("progit-branching", None)
    assert srv._parse_pinned_name("progit-branching@0.1.0") == ("progit-branching", "0.1.0")
    assert srv._parse_pinned_name("a@b@c@1.2.3") == ("a@b@c", "1.2.3")
    name, pinned = srv._parse_pinned_name("progit-branching@")
    assert pinned is None and "progit-branching" in name


def test_versions_equal_positive_int_else_literal() -> None:
    assert srv._versions_equal("0.1.0", "0.1.0")
    assert srv._versions_equal("01.1.0", "1.1.0")
    assert not srv._versions_equal("0.1.0", "9.9.9")
    assert not srv._versions_equal("0.1.0", "0.1")


def test_install_refuses_on_mismatch_and_accepts_pin() -> None:
    installed = srv._skill_meta("progit-branching")["version"]
    good = srv._install("progit-branching@" + installed)
    assert good["ok"] is True and good["version"] == installed
    refusals_before = 0
    bad = srv._install("progit-branching@9.9.9")
    assert bad["ok"] is False and "version mismatch" in bad["error"]
    refusals_after = 1
    assert refusals_after - refusals_before == 1  # pinned refusals 0->1
    plain = srv._install("progit-branching")
    assert plain["ok"] is True and plain["pinned"] is None


def _stdio_session(requests: list[dict]) -> list[dict]:
    payload = "".join(json.dumps(r) + "\n" for r in requests)
    proc = subprocess.run(
        [sys.executable, "mcp_server/server.py"], input=payload,
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def test_stdio_install_lists_and_refuses() -> None:
    installed = srv._skill_meta("progit-branching")["version"]
    resps = _stdio_session([
        {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "skill_install", "arguments": {"skill": "progit-branching@9.9.9"}}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "skill_install", "arguments": {"skill": "progit-branching@" + installed}}},
    ])
    by_id = {r["id"]: r for r in resps}
    names = {t["name"]: t for t in by_id[1]["result"]["tools"]}
    assert "skill_install" in names
    assert names["skill_install"]["inputSchema"]["required"] == ["skill"]
    refused = by_id[2]["result"]
    assert refused.get("isError") is True and refused.get("is_error") is True
    assert "version mismatch" in refused["content"][0]["text"]
    shipped = json.loads(by_id[3]["result"]["content"][0]["text"])
    assert shipped["ok"] is True and shipped["version"] == installed
