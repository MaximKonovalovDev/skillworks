"""bat-cat: the paging cat clone, the pager precedence, and the 4 run commands really run.

Offline tests (default run): pairs.json shape, pairs.md freshness, every
SKILL.md rule line carrying its [src:] anchor, every trial and QA must-word
literally present in the skill text, the d9559c69 pin, the token budget.
Live tests (SKILL_LIVE=1, they run real pwsh plus rg): all 12 pairs through
scripts/run_bat.py, the 4 pinned rg replays, the harness-can-fail probe, the
red replay (wrong-file query fails, fixed query passes), and an installed
copy driven through pwsh.
"""
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g
import skill_stock as stock
from skill_gates import live

NAME = "bat-cat"
SKILL = g.SKILLS / NAME
SCRIPTS = SKILL / "scripts"
PAIRS = SKILL / "references" / "pairs.json"
PIN = "d9559c69"

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")
needs_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh 7 is not installed")
needs_rg = pytest.mark.skipif(shutil.which("rg") is None, reason="rg is not installed")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(f"bat_cat_{name}", SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"bat_cat_{name}"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def doc() -> dict:
    return json.loads(PAIRS.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def results(doc: dict) -> dict:
    if shutil.which("pwsh") is None:
        pytest.skip("pwsh 7 is not installed")
    return {r["id"]: r for r in _load("run_bat").run_pairs(doc)}


def test_pair_file_is_well_formed(doc: dict) -> None:
    ids = [p["id"] for p in doc["pairs"]]
    assert len(ids) == len(set(ids)) >= 12
    for p in doc["pairs"]:
        assert p.get("good") and (p.get("expect") or p.get("expect_regex")), p["id"]
        assert p.get("bad") is not None, p["id"]
        assert p.get("bad_silent") or p.get("bad_error"), f"{p['id']}: say how bad fails"


def test_pairs_md_is_current() -> None:
    assert _load("pairs_to_md").main(["--check"]) == 0


def test_pairs_md_covers_every_pair(doc: dict) -> None:
    text = (SKILL / "references" / "pairs.md").read_text(encoding="utf-8")
    for p in doc["pairs"]:
        assert f"### {p['id']}" in text, p["id"]
    assert text.count("prints:") >= 12


def test_every_rule_line_carries_a_source(doc: dict) -> None:
    ids = {p["id"] for p in doc["pairs"]}
    body = g.body_of((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    rules = [ln for ln in body.splitlines() if re.match(r"^\s*[-*]\s+.*`[^`]+`.*$", ln)]
    assert len(rules) == 12, f"{len(rules)} rule lines, want 12"
    missing = [ln for ln in rules if not ln.rstrip().endswith("]") or "[src:" not in ln]
    assert not missing, f"rule lines without a trailing [src: ...]: {missing[:3]}"
    anchors = set(re.findall(r"references/pairs\.md#(bt-p\d+)", body))
    assert anchors <= ids, f"anchors without a pair: {sorted(anchors - ids)}"
    assert len(anchors) == 12, f"only {len(anchors)} pair anchors"


def _skill_text() -> str:
    return g.skill_text(NAME).lower()


def test_trial_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for line in (g.ROOT / "evals" / f"{NAME}_trials.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row.get("must", []):
            assert m.lower() in text, f"must {m!r} is not in the skill text (task: {row['id']})"


def test_qa_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for line in (g.ROOT / "evals" / f"{NAME}_qa.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row["must"]:
            assert m.lower() in text, f"must {m!r} is not in the skill text (question: {row['q']})"


def test_pin_is_the_same_in_every_file() -> None:
    for f in ("SKILL.md", "references/sources.md"):
        assert PIN in (SKILL / f).read_text(encoding="utf-8"), f"{f} must name {PIN}"


def test_skill_body_within_budget() -> None:
    assert g.body_tokens((SKILL / "SKILL.md").read_text(encoding="utf-8")) <= g.BODY_TOKEN_BUDGET


def test_ascii_only_and_no_private_paths() -> None:
    for p in sorted(SKILL.rglob("*")):
        if not p.is_file() or p.suffix not in {".md", ".py", ".json", ".jsonl"}:
            continue
        if "export" in p.relative_to(SKILL).parts or "__pycache__" in p.parts:
            continue
        t = p.read_text(encoding="utf-8")
        bad = sorted({c for c in t if ord(c) > 126})
        assert not bad, f"{p.name} has non-ASCII characters {bad[:5]}"
        assert not re.search(r"[A-Za-z]:\\Users\\|/Users/[a-z]|ghp_|github_pat_", t), (
            f"{p.name} has a private path or token-like text")


def test_distill_check_passes() -> None:
    from book2skill import distill as distill_mod
    report = distill_mod.check(SKILL)
    assert report["ok"], f"distill findings: {report['findings']}"


def _rg(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["rg", *args], cwd=g.ROOT, capture_output=True, text=True)


@live
@needs_rg
def test_live_syntax_highlighting_lines() -> None:
    r = _rg("-n", "syntax highlighting", "work/bat-cat/src/README.md")
    assert r.returncode == 0
    lines = r.stdout.splitlines()
    assert len(lines) == 9, r.stdout[:400]
    assert lines[0].startswith("6:")
    assert lines[2].startswith("137:")
    assert "cat(1)" in r.stdout


@live
@needs_rg
def test_live_line_numbers_lines() -> None:
    r = _rg("-n", "line numbers", "work/bat-cat/src/README.md")
    assert r.returncode == 0
    lines = r.stdout.splitlines()
    assert len(lines) == 7, r.stdout[:400]
    assert lines[0].startswith("94:")
    assert lines[2].startswith("506:")
    assert "bat -n" in r.stdout


@live
@needs_rg
def test_live_pager_lines() -> None:
    r = _rg("-n", "Pager", "work/bat-cat/src/pager.rs")
    assert r.returncode == 0
    lines = r.stdout.splitlines()
    assert len(lines) == 28, r.stdout[:400]
    assert lines[0].startswith("6:")
    assert lines[2].startswith("14:")
    assert "enum PagerSource" in r.stdout


@live
@needs_rg
def test_live_bat_pager_lines() -> None:
    r = _rg("-n", "BAT_PAGER", "work/bat-cat/src/README.md")
    assert r.returncode == 0
    lines = r.stdout.splitlines()
    assert len(lines) == 7, r.stdout[:400]
    assert lines[0].startswith("647:")
    assert "builtin" in r.stdout


@live
@needs_pwsh
def test_every_pair_behaves_as_written(results: dict) -> None:
    bad = {k: v["why"] for k, v in results.items() if v["bad_ok"] is False or v["good_ok"] is False}
    assert not bad, bad
    assert len(results) >= 12, f"only {len(results)} pairs ran"


@live
@needs_pwsh
def test_the_harness_can_fail() -> None:
    """A pair whose bad command works, and whose good command prints the wrong thing, must be reported."""
    doc = {
        "fixture": {"plain.txt": "hello\n"},
        "pairs": [{"id": "liar", "group": "x", "bad": "rg -n \"BAT_PAGER\" plain.txt",
                   "bad_error": "missed BAT_PAGER",
                   "good": "rg -n \"BAT_PAGER\" plain.txt", "expect": "NOT THERE"}],
    }
    res = _load("run_bat").run_pairs(doc)[0]
    assert res["bad_ok"] is False and res["good_ok"] is False


@live
@needs_pwsh
def test_error_fragments_come_from_real_failures(results: dict) -> None:
    text = (SKILL / "references" / "errors.md").read_text(encoding="utf-8")
    rows = re.findall(r"^- `(.+?)`: .*?Pair `([\w-]+)`", text, re.M)
    assert len(rows) >= 12
    for fragment, pair_id in rows:
        got = results[pair_id]["bad_text"]
        assert fragment.lower() in got.lower(), f"errors.md says {fragment!r} for {pair_id}, the real error was {got.strip()[:200]!r}"


@live
@needs_rg
def test_red_replay_wrong_file_fails_fixed_file_passes() -> None:
    """The packet red replay: the highlight phrase lives in README.md, not the pager file."""
    red = _rg("-n", "syntax highlighting", "work/bat-cat/src/pager.rs")
    assert red.returncode == 1 and red.stdout == ""
    green = _rg("-n", "syntax highlighting", "work/bat-cat/src/README.md")
    assert green.returncode == 0 and green.stdout.splitlines()[0].startswith("6:")


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run its script from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, NAME, "scripts/run_bat.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--pair" in said
    copy.assert_nothing_written_elsewhere()
