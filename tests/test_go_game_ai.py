"""go-game-ai: planes plus MCTS ideas from b1-gogame, no nets at runtime.

Offline tests (default run): QA file has 12 rows, trials file has 12 answer rows,
every must word appears in the skill text, frontmatter names the skill,
body within budget, sources carry URL plus verified plus licence, ASCII only,
eval rate 0.6 or more, trial proof 12 runs with 0.8 or more and lift 0.3 or more.
"""
import json
import re
from pathlib import Path

import pytest

NAME = "go-game-ai"
ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / NAME
QA = ROOT / "evals" / (NAME + "_qa.jsonl")
TRIALS = ROOT / "evals" / (NAME + "_trials.jsonl")

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")


def _skill_text():
    out = []
    for path in sorted(SKILL.rglob("*.md")):
        rel = path.relative_to(SKILL)
        if path.name in ("eval_report.json", "trial-proof.json", "live-proof.json"):
            continue
        if "export" in rel.parts or "demo" in rel.parts:
            continue
        if path.suffix != ".md":
            continue
        out.append(path.read_text(encoding="utf-8"))
    return "\n".join(out).lower()


def _frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    assert m, "SKILL.md needs frontmatter"
    out = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([\w-]+):\s*(.*)$", line.strip())
        if kv:
            out[kv.group(1)] = kv.group(2).strip()
    return out


def test_qa_file_has_twelve_rows():
    rows = [json.loads(ln) for ln in QA.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) == 12, "want 12 QA rows, have %d" % len(rows)
    for row in rows:
        assert isinstance(row.get("q"), str) and row["q"].strip()
        assert isinstance(row.get("must"), list) and all(isinstance(s, str) and s for s in row["must"])


def test_trials_file_has_twelve_answer_rows():
    rows = [json.loads(ln) for ln in TRIALS.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) == 12, "want 12 trial rows, have %d" % len(rows)
    ids = [r.get("id") for r in rows]
    assert len(set(ids)) == 12, "trial ids must be unique"
    for row in rows:
        assert row.get("kind") == "answer", "checklist skill uses answer rows"
        assert isinstance(row.get("task"), str) and row["task"].strip()
        assert isinstance(row.get("must"), list) and all(isinstance(s, str) and s for s in row["must"])


def test_qa_musts_literally_appear_in_the_skill_text():
    text = _skill_text()
    for line in QA.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row["must"]:
            assert m.lower() in text, "must %r is not in the skill text" % m


def test_trial_musts_literally_appear_in_the_skill_text():
    text = _skill_text()
    for line in TRIALS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row.get("must", []):
            assert m.lower() in text, "must %r is not in the skill text" % m


def test_frontmatter_names_the_skill():
    fm = _frontmatter()
    assert fm.get("name") == NAME
    desc = fm.get("description", "")
    assert 40 <= len(desc) <= 1024
    assert re.search(r"\bUse (when|before|whenever|for)\b", desc)
    assert fm.get("license"), "licence line missing"


def test_skill_body_within_budget():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    body = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)
    assert len(body) // 4 + 10 <= 2000, "SKILL.md body over 2000 tokens"


def test_sources_have_url_verified_licence():
    text = (SKILL / "references" / "sources.md").read_text(encoding="utf-8")
    assert "https://" in text and "verified" in text.lower()
    assert "MIT" in text or "licence" in text.lower() or "license" in text.lower()


def test_ascii_only_and_no_private_paths():
    for p in sorted(SKILL.rglob("*")):
        if not p.is_file() or p.suffix not in (".md", ".py", ".json", ".jsonl"):
            continue
        if "export" in p.relative_to(SKILL).parts:
            continue
        if p.name in ("live-proof.json", "trial-proof.json", "eval_report.json"):
            continue
        t = p.read_text(encoding="utf-8")
        bad = sorted({c for c in t if ord(c) > 126})
        assert not bad, "%s has non-ASCII %s" % (p.name, bad[:5])
        assert not re.search(r"[A-Za-z]:\\Users\\|/Users/[a-z]|ghp_|github_pat_", t)


def test_eval_rate_meets_gate():
    report = json.loads((SKILL / "eval_report.json").read_text(encoding="utf-8"))
    assert report["total"] == 12
    assert report["rate"] >= 0.6, "eval rate %s below 0.6" % report["rate"]


def test_trial_proof_meets_gate():
    proof = json.loads((SKILL / "references" / "trial-proof.json").read_text(encoding="utf-8"))
    assert proof["runs"] >= 12
    assert proof["with_rate"] >= 0.8, "with_rate %s below 0.8" % proof["with_rate"]
    assert proof["lift"] >= 0.3, "lift %s below 0.3" % proof["lift"]
    assert proof["ok"] is True
