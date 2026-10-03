"""K-29 (P2-SCHEMA-1001): signature-derived inputSchema + CacheHint + validation.

Stays clear of tests/test_pipeline.py (claimed by K-28 run); proves the
row's done-when: tools/list shows inputSchema query/skill/limit, bad call
returns is_error envelope, pytest stays green.
"""
import inspect
import json
import subprocess
import sys
from pathlib import Path

import mcp_server.server as srv


def test_input_schema_derived_from_search_signature() -> None:
    sig = inspect.signature(srv._search)
    assert list(sig.parameters) == ["query", "skill", "limit"]
    schema = srv.INPUT_SCHEMA
    assert schema["type"] == "object"
    assert set(schema["properties"]) == {"query", "skill", "limit"}
    assert schema["required"] == ["query"]
    assert schema["properties"]["query"]["type"] == "string"
    assert schema["properties"]["limit"]["type"] == "integer"
    assert schema["properties"]["limit"]["minimum"] == 1
    assert schema["properties"]["limit"]["maximum"] == 20
    assert srv.CACHE_HINT == {"ttlMs": 3600000, "scope": "public"}


def test_validate_args_accepts_good_rejects_bad() -> None:
    ok, cleaned = srv._validate_args({"query": "branching git"})
    assert ok and cleaned["limit"] == 5
    for bad in ({}, {"query": ""}, {"query": "  "}, {"query": 5},
                {"query": "git", "limit": 0}, {"query": "git", "limit": 999},
                {"query": "git", "limit": "abc"}, {"query": "git", "skill": 7}):
        ok, _ = srv._validate_args(bad)
        assert not ok, bad


def _stdio_session(requests: list[dict]) -> list[dict]:
    payload = "".join(json.dumps(r) + "\n" for r in requests)
    proc = subprocess.run(
        [sys.executable, "mcp_server/server.py"], input=payload,
        capture_output=True, text=True, timeout=30,
    )
    assert proc.returncode == 0, proc.stderr
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def test_stdio_handshake_list_call_and_bad_call() -> None:
    resps = _stdio_session([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "skill_search", "arguments": {"query": "branching git"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "tools/call",
         "params": {"name": "skill_search", "arguments": {"query": "branching git", "limit": 999}}},
        {"jsonrpc": "2.0", "id": 5, "method": "tools/call",
         "params": {"name": "skill_search", "arguments": {}}},
    ])
    by_id = {r["id"]: r for r in resps}
    assert "result" in by_id[1]  # handshake
    tools = by_id[2]["result"]["tools"]
    assert tools[0]["name"] == "skill_search"
    schema = tools[0]["inputSchema"]
    assert set(schema["properties"]) >= {"query", "skill", "limit"}
    assert "query" in schema["required"]
    # good call: legacy content.text still present
    good = by_id[3]["result"]
    assert good["content"][0]["type"] == "text"
    # bad calls: typed is_error envelope (both casings for clients)
    for bid in (4, 5):
        bad = by_id[bid]["result"]
        assert bad.get("isError") is True and bad.get("is_error") is True
        assert bad["content"][0]["type"] == "text"
