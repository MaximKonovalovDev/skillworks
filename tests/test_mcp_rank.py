"""K-15 + K-19 (R3 ranked search): rank fields + gate-first sort + trust fields."""
import json
import subprocess
import sys

import mcp_server.server as srv


def test_ranked_search_progit_before_freud_with_rank_and_trust_fields() -> None:
    """Gate-first ordering: progit-branching (1.0) before freud (0.50) with new fields."""
    hits = srv._search("built owned sources skill", limit=20)
    skills = [h["skill"] for h in hits]
    assert "progit-branching" in skills and "freud-dream-psychology" in skills
    assert skills.index("progit-branching") < skills.index("freud-dream-psychology")
    # gate-first: every above-gate hit precedes every below-gate hit
    seen_below = False
    for h in hits:
        if not h["above_gate"]:
            seen_below = True
        elif seen_below:
            raise AssertionError("above-gate hit sorted after below-gate hit")
    first = next(h for h in hits if h["skill"] == "progit-branching")
    last = next(h for h in hits if h["skill"] == "freud-dream-psychology")
    for h in (first, last):
        for field in ("version", "author", "downloads", "installs", "stars",
                      "tags", "verified", "eval_rate", "above_gate", "installed"):
            assert field in h, field
        assert isinstance(h["tags"], list)
    assert first["eval_rate"] == 1.0 and last["eval_rate"] == 0.5
    assert first["above_gate"] is True and last["above_gate"] is False
    assert first["verified"] is True and last["verified"] is False
    assert first["installed"] is True and last["installed"] is True
    assert first["installs"] == 1 and first["downloads"] > last["downloads"]
    # stdio proof: handshake + skill_search keeps progit first with new fields
    payload = "".join(json.dumps(r) + "\n" for r in [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "skill_search",
                    "arguments": {"query": "built owned sources skill", "limit": 20}}},
    ])
    proc = subprocess.run([sys.executable, "mcp_server/server.py"], input=payload,
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    by_id = {json.loads(ln)["id"]: json.loads(ln)
             for ln in proc.stdout.splitlines() if ln.strip()}
    assert "result" in by_id[1]
    wire = json.loads(by_id[2]["result"]["content"][0]["text"])
    wskills = [h["skill"] for h in wire]
    assert wskills.index("progit-branching") < wskills.index("freud-dream-psychology")
    assert wire[0]["version"] and wire[0]["author"] and "verified" in wire[0]
