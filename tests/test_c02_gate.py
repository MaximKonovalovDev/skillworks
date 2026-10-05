"""C-02 golden-set gate for skill_search.

Three calls from mcp_server/c02-goldens.json. Live first; tmp fixture
only when the live skills dir gives nothing. Mode is printed honestly.
Timestamps are masked before any compare so the gate is stable.
"""
import json
import os
import re
from pathlib import Path

import mcp_server.server as srv

GOLDENS = Path(__file__).resolve().parent.parent / "mcp_server" / "c02-goldens.json"

_TS = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?|\b1[0-9]{12}\b")


def _mask(text: str) -> str:
    return _TS.sub("<ts>", text)


def _norm(hits: list[dict]) -> list[dict]:
    out = []
    for h in hits:
        out.append({
            "skill": h.get("skill"),
            "file": str(h.get("file")).replace("\\", "/"),
            "score": h.get("score"),
            "head": _mask(str(h.get("head", ""))[:80]),
            "version": h.get("version"),
            "author": h.get("author"),
            "downloads": h.get("downloads"),
            "installs": h.get("installs"),
            "stars": h.get("stars"),
            "tags": h.get("tags"),
            "verified": h.get("verified"),
            "eval_rate": h.get("eval_rate"),
            "above_gate": h.get("above_gate"),
            "installed": h.get("installed"),
        })
    return out


def _make_fixture(tmp: Path) -> Path:
    base = tmp / "c02-skills"
    a = base / "progit-branching"
    b = base / "other-skill"
    a.mkdir(parents=True)
    b.mkdir(parents=True)
    (a / "SKILL.md").write_text("# progit-branching\nbranching git merge skill\n", encoding="utf-8")
    (a / "notes.md").write_text("git branching deep notes branching git\n", encoding="utf-8")
    (b / "SKILL.md").write_text("# other-skill\nunrelated notes here\n", encoding="utf-8")
    return base


def _run(args: dict, tmp: Path) -> tuple[list[dict], str]:
    ok, cleaned = srv._validate_args(args)
    assert ok, f"golden args fail validation: {args}"
    try:
        hits = srv._search(cleaned["query"], cleaned["skill"], cleaned["limit"])
        if hits:
            return hits, "live"
    except OSError:
        pass
    if not srv._skills():
        base = _make_fixture(tmp)
        os.environ["SKILLWORKS_SKILLS_DIR"] = str(base)
        hits = srv._search(cleaned["query"], cleaned["skill"], cleaned["limit"])
        return hits, "fixture"
    return srv._search(cleaned["query"], cleaned["skill"], cleaned["limit"]), "live"


def test_c02_golden_gate(tmp_path: Path, capsys) -> None:
    spec = json.loads(GOLDENS.read_text(encoding="utf-8"))
    assert spec["tool"] == "skill_search"
    assert len(spec["calls"]) == 3
    modes: set[str] = set()
    for call in spec["calls"]:
        hits, mode = _run(dict(call["arguments"]), tmp_path)
        modes.add(mode)
        normed = _norm(hits)
        masked = json.loads(_mask(json.dumps(normed, ensure_ascii=False)))
        base = call["baseline"]
        if base.get("expect_empty"):
            assert masked == [], f"{call['id']}: want empty, got {len(masked)} hits"
            continue
        assert len(masked) >= int(base.get("min_hits", 1)), f"{call['id']}: no hits"
        assert len(masked) <= int(call["arguments"].get("limit", 5)), f"{call['id']}: over limit"
        assert masked[0]["skill"] == base["top_skill"], f"{call['id']}: top {masked[0]['skill']}"
        if base.get("only_skill"):
            assert all(h["skill"] == base["only_skill"] for h in masked), call["id"]
        for field in base.get("required_fields", []):
            assert field in masked[0], f"{call['id']}: missing {field}"
    os.environ.pop("SKILLWORKS_SKILLS_DIR", None)
    with capsys.disabled():
        print(f"C02 gate: mode={'/'.join(sorted(modes))}")
