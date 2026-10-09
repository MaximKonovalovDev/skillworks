"""K-15 + K-19 (R3 ranked search): rank fields + gate-first sort + trust fields."""
import json
import subprocess
import sys

import mcp_server.server as srv


def test_ranked_search_progit_before_freud_with_rank_and_trust_fields() -> None:
    """Gate-first sort + trust fields on a narrow 'branching' fixture (limit 8)."""
    for name in ("progit-branching", "freud-dream-psychology"):
        probe = srv._search("skill", skill=name, limit=3)
        assert probe, name
        assert len(probe) <= 3
        for h in probe:
            for field in ("version", "author", "downloads", "installs", "stars",
                          "tags", "verified", "eval_rate", "above_gate", "installed",
                          "skill", "file", "score", "head"):
                assert field in h, field
            assert h["skill"] == name
            assert isinstance(h["tags"], list)
            assert h["score"] > 0
            assert h["above_gate"] is True and h["verified"] is True
            assert h["installed"] is True and h["installs"] == 1
            assert h["eval_rate"] >= 0.6
            assert h["stars"] == round(h["eval_rate"] * 5, 1)
            assert h["version"] and h["author"]
    hits = srv._search("branching", limit=8)
    assert len(hits) <= 8
    skills = [h["skill"] for h in hits]
    assert "progit-branching" in skills and "freud-dream-psychology" in skills
    assert skills.index("progit-branching") < skills.index("freud-dream-psychology")
    seen_below = False
    for h in hits:
        if not h["above_gate"]:
            seen_below = True
        elif seen_below:
            raise AssertionError("above-gate hit sorted after below-gate hit")
    keys = [(h["above_gate"], h["installed"], h["downloads"], h["score"]) for h in hits]
    assert keys == sorted(keys, reverse=True)
    payload = "".join(json.dumps(r) + "\n" for r in [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
         "params": {"name": "skill_search",
                    "arguments": {"query": "branching", "limit": 8}}},
    ])
    proc = subprocess.run([sys.executable, "mcp_server/server.py"], input=payload,
                          capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stderr
    by_id = {json.loads(ln)["id"]: json.loads(ln)
             for ln in proc.stdout.splitlines() if ln.strip()}
    assert "result" in by_id[1]
    wire = json.loads(by_id[2]["result"]["content"][0]["text"])
    assert len(wire) <= 8
    wskills = [h["skill"] for h in wire]
    assert "progit-branching" in wskills and "freud-dream-psychology" in wskills
    assert wskills.index("progit-branching") < wskills.index("freud-dream-psychology")
    assert wire[0]["version"] and wire[0]["author"] and "verified" in wire[0]
    assert wire[0]["stars"] == round(wire[0]["eval_rate"] * 5, 1)
