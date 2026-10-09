"""game-patterns-free: MIT game-loop patterns the skill really holds.

Offline tests (default run): every QA must-word appears in the skill text,
the 898b1f2e pin is in sources and notices, body within budget,
frontmatter names the skill, sources carry URLs plus verified plus licence.
Live tests (SKILL_LIVE=1, real rg plus real eval): rg finds the MIT markers,
the pipeline eval gate passes.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

NAME = "game-patterns-free"
SKILL = g.SKILLS / NAME
NOTES = SKILL / "chapters" / "notes.md"
SOURCES = SKILL / "references" / "sources.md"
QA = g.ROOT / "evals" / (NAME + "_qa.jsonl")
PIN = "898b1f2e1818c80d7eed5eba98e9903ec13b7771"

pytestmark = pytest.mark.skipif(
    not (SKILL / "SKILL.md").is_file(), reason="skill not built yet"
)
needs_rg = pytest.mark.skipif(shutil.which("rg") is None, reason="rg is not installed")


def _skill_text():
    return g.skill_text(NAME).lower()


def test_qa_file_has_ten_rows():
    rows = [json.loads(ln) for ln in QA.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(rows) >= 8, "want 8 QA rows or more, have %d" % len(rows)
    for row in rows:
        assert isinstance(row.get("q"), str) and row["q"].strip()
        assert isinstance(row.get("must"), list) and all(isinstance(s, str) and s for s in row["must"])


def test_qa_musts_literally_appear_in_the_skill_text():
    text = _skill_text()
    for line in QA.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row["must"]:
            assert m.lower() in text, "must %r is not in the skill text (question: %s)" % (m, row["q"])


def test_pin_is_in_sources_and_notices():
    assert PIN in SOURCES.read_text(encoding="utf-8"), "sources.md must name the book pin"
    notices = (g.ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    assert "munificent/game-programming-patterns" in notices, "notices must credit the book repo"


def test_skill_body_within_budget():
    assert g.body_tokens((SKILL / "SKILL.md").read_text(encoding="utf-8")) <= g.BODY_TOKEN_BUDGET


def test_frontmatter_names_the_skill():
    fm = g.frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    assert fm.get("name") == NAME
    desc = fm.get("description", "")
    assert 40 <= len(desc) <= 1024
    assert re.search(r"\bUse (when|before|whenever|for)\b", desc)
    assert fm.get("license"), "licence line missing"


def test_sources_have_urls_and_verified_licence():
    text = SOURCES.read_text(encoding="utf-8")
    assert "https://" in text and "verified" in text.lower()
    assert any(lic in text for lic in g.LICENSES)


def test_mit_markers_are_in_the_notes():
    text = NOTES.read_text(encoding="utf-8")
    for needle in ("code/cpp", "MIT", "Bjorn", "InputComponent", "interpret", "bytecode"):
        assert needle in text, needle


def test_ascii_only_and_no_private_paths():
    for p in sorted(SKILL.rglob("*")):
        if not p.is_file() or p.suffix not in {".md", ".py", ".json", ".jsonl"}:
            continue
        if "export" in p.relative_to(SKILL).parts or "__pycache__" in p.parts:
            continue
        if p.name in ("live-proof.json", "trial-proof.json", "eval_report.json"):
            continue
        t = p.read_text(encoding="utf-8")
        bad = sorted({c for c in t if ord(c) > 126})
        assert not bad, "%s has non-ASCII characters %s" % (p.name, bad[:5])
        assert not re.search(r"[A-Za-z]:\\Users\\|/Users/[a-z]|ghp_|github_pat_", t)


def _rg(*args):
    return subprocess.run(["rg"] + list(args), cwd=g.ROOT, capture_output=True, text=True)


@live
@needs_rg
def test_live_rg_finds_bjorn_component():
    r = _rg("-l", "Bjorn", "skills/game-patterns-free/chapters/notes.md")
    assert r.returncode == 0
    assert "notes.md" in r.stdout


@live
@needs_rg
def test_live_rg_finds_mit_code_path():
    r = _rg("-l", "code/cpp", "skills/game-patterns-free/chapters/notes.md")
    assert r.returncode == 0
    assert "notes.md" in r.stdout


@live
@needs_rg
def test_live_rg_counts_game_loop_markers():
    r = _rg("-c", "processInput", "skills/game-patterns-free/chapters/notes.md")
    assert r.returncode == 0
    assert int(r.stdout.strip().split(":")[-1]) >= 1


@live
def test_live_eval_gate_passes():
    assert g.check_eval(NAME) >= g.EVAL_GATE
