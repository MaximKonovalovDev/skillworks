"""handsrust-code: the rules, the files they name, and the 3 pairs really run.

Offline tests (default run): pairs.json shape, pairs.md freshness, every
SKILL.md rule line carrying its [src:] anchor, every trial and QA must-word
literally present in the skill text, and the token budget.
Live tests (SKILL_LIVE=1, they run real cargo): all 3 pairs through
scripts/handsrust_code.py, the harness-can-fail probe, and an installed copy
driven through pwsh.
"""
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

import skill_gates as g
import skill_stock as stock
from skill_gates import live

NAME = "handsrust-code"
SKILL = g.SKILLS / NAME
SCRIPTS = SKILL / "scripts"
PAIRS = SKILL / "references" / "pairs.json"

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")
needs_cargo = pytest.mark.skipif(shutil.which("cargo") is None, reason="cargo is not installed")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"handsrust_code_{name}", SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"handsrust_code_{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def doc() -> dict:
    return json.loads(PAIRS.read_text(encoding="utf-8"))


def test_pair_file_is_well_formed(doc: dict) -> None:
    ids = [p["id"] for p in doc["pairs"]]
    assert len(ids) == len(set(ids)) == 3, ids
    assert set(ids) == {"hr-p01", "hr-p02", "hr-p03"}, ids
    for p in doc["pairs"]:
        assert p.get("group"), p["id"]
        assert p.get("title"), p["id"]
        assert p.get("good") and p["good"].get("steps"), p["id"]
        for side in ("good", "bad"):
            for step in p.get(side, {}).get("steps", []):
                assert "argv" in step or "write" in step or "assert_contains" in step \
                    or "assert_exists" in step or "assert_absent" in step, (p["id"], step)
    goods = [s for p in doc["pairs"] for s in p["good"]["steps"] if "argv" in s and s["argv"][:2] == ["cargo", "test"]]
    assert goods, "good sides must run cargo test"
    for s in goods:
        assert s.get("expect_exit", 0) == 0
        low = [e.lower() for e in s.get("expect", [])]
        assert "test result: ok" in low, s
        assert any("3 passed" in e for e in low), s
    bads = [s for p in doc["pairs"] for s in p["bad"]["steps"] if "argv" in s and s["argv"][:2] == ["cargo", "test"]]
    assert len(bads) == 3, "every bad side must run cargo test"
    for s in bads:
        assert s.get("expect_exit") == 101, s
        assert any("failed" in e.lower() for e in s.get("expect", [])), s


def test_pairs_md_is_current() -> None:
    assert _load("pairs_to_md").main(["--check"]) == 0


def test_pairs_md_covers_every_pair(doc: dict) -> None:
    text = (SKILL / "references" / "pairs.md").read_text(encoding="utf-8")
    for p in doc["pairs"]:
        assert f"### {p['id']}" in text, p["id"]


def test_every_rule_line_carries_a_source(doc: dict) -> None:
    ids = {p["id"] for p in doc["pairs"]}
    body = g.body_of((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    rules = [ln for ln in body.splitlines() if re.match(r"^\s*[-*]\s+.*`[^`]+`.*$", ln)]
    assert len(rules) >= 6, f"only {len(rules)} rule lines"
    missing = [ln for ln in rules if not ln.rstrip().endswith("]") or "[src:" not in ln]
    assert not missing, f"rule lines without a trailing [src: ...]: {missing[:3]}"
    anchors = set(re.findall(r"references/pairs\.md#(hr-p\d+)", body))
    assert anchors <= ids, f"anchors without a pair: {sorted(anchors - ids)}"
    assert len(anchors) >= 3, f"only {len(anchors)} pair anchors"
    assert anchors == ids, f"anchors {sorted(anchors)} do not cover {sorted(ids)}"


def _skill_text() -> str:
    return g.skill_text(NAME).lower()


def test_trial_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for line in (g.ROOT / "evals" / "handsrust-code_trials.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row.get("must", []):
            assert m.lower() in text, f"must {m!r} is not in the skill text (task: {row.get('id')})"


def test_qa_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for line in (g.ROOT / "evals" / "handsrust-code_qa.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row["must"]:
            assert m.lower() in text, f"must {m!r} is not in the skill text (question: {row['q']})"


def test_skill_body_within_budget() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert g.body_tokens(text) <= g.BODY_TOKEN_BUDGET


def test_no_private_paths_in_the_public_skill() -> None:
    for p in SKILL.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py"}:
            t = p.read_text(encoding="utf-8")
            assert not re.search(r"[A-Za-z]:\\Users\\|/Users/[a-z]|ghp_|github_pat_", t), f"{p.name} has a private path or token-like text"


@live
@needs_cargo
def test_every_pair_behaves_as_written(doc: dict) -> None:
    results = _load("handsrust_code").run_pairs(doc)
    bad = {r["id"]: (r["good_note"], r["bad_note"]) for r in results if not r["ok"]}
    assert not bad, bad
    assert len(results) == 3, f"only {len(results)} pairs ran"


@live
@needs_cargo
def test_the_harness_can_fail() -> None:
    """A pair whose bad command works, and whose good command prints the wrong thing, must be reported."""
    doc = {
        "pairs": [{"id": "liar", "title": "liar", "bad": {"steps": [
            {"argv": ["cargo", "--version"], "expect": ["cargo"], "expect_exit": 0}]}, "good": {"steps": [
            {"argv": ["cargo", "--version"], "expect": ["NOT THERE"], "expect_exit": 0}]}}],
    }
    res = _load("handsrust_code").run_pairs(doc)[0]
    assert res["bad_ok"] is True and res["good_ok"] is False


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run its script from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, NAME, "scripts/handsrust_code.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--pair" in said
    copy.assert_nothing_written_elsewhere()
