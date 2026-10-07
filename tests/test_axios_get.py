"""axios-get: the codes, the files they name, and the 4 run commands really run.

Offline tests (default run): every SKILL.md rule bullet is covered by the
trial pool, every trial must-word literally appears in the skill text,
the 2b169bbb pin, the token budget, ASCII only, no private paths, and the
distill gate passes.
Live tests (SKILL_LIVE=1, they run real rg): the 4 run tasks replay exit 0
with the pinned outputs, plus the harness-can-fail probe.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

NAME = "axios-get"
SKILL = g.SKILLS / NAME
PIN = "2b169bbb"

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")
needs_rg = pytest.mark.skipif(shutil.which("rg") is None, reason="rg is not installed")


def _body() -> str:
    return g.body_of((SKILL / "SKILL.md").read_text(encoding="utf-8"))


def _rules() -> list:
    return [ln for ln in _body().splitlines() if re.match(r"^\s*[-*]\s+.*`[^`]+`.*$", ln)]


def _skill_text() -> str:
    return g.skill_text(NAME).lower()


def _sheet() -> list:
    return [json.loads(ln) for ln in
            (g.ROOT / "evals" / f"{NAME}_trials.jsonl").read_text(encoding="utf-8").splitlines()
            if ln.strip()]


def test_rule_bullets_fit_the_trial_pool() -> None:
    trials = _sheet()
    assert len(trials) >= 12, f"only {len(trials)} trial rows"
    assert 1 <= len(_rules()) <= len(trials), (
        f"{len(_rules())} rule bullets but {len(trials)} trial locators")


def test_trial_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for row in _sheet():
        for m in row.get("must", []):
            assert m.lower() in text, f"must {m!r} is not in the skill text (task: {row['id']})"


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
def test_live_cancel_code_line() -> None:
    r = _rg("-n", "ERR_CANCELED", "work/axios-get/src/CanceledError.js")
    assert r.returncode == 0
    lines = r.stdout.splitlines()
    assert len(lines) == 1, r.stdout[:400]
    assert lines[0].startswith("16:")
    assert "AxiosError.ERR_CANCELED" in r.stdout
    assert "'canceled'" in r.stdout


@live
@needs_rg
def test_live_timeout_static_lines() -> None:
    r = _rg("-n", "ECONNABORTED", "work/axios-get/src/AxiosError.js")
    assert r.returncode == 0
    lines = r.stdout.splitlines()
    assert len(lines) == 2, r.stdout[:400]
    assert "206:AxiosError.ECONNABORTED = 'ECONNABORTED';" in r.stdout
    assert "AxiosError" in r.stdout


@live
@needs_rg
def test_live_flag_line() -> None:
    r = _rg("-n", "isAxiosError", "work/axios-get/src/AxiosError.js")
    assert r.returncode == 0
    assert "161:    this.isAxiosError = true;" in r.stdout


@live
@needs_rg
def test_live_file_list_names_one_file() -> None:
    r = _rg("-l", "CanceledError", "work/axios-get/src/")
    assert r.returncode == 0
    assert r.stdout.strip().replace("\\", "/") == "work/axios-get/src/CanceledError.js"


@live
@needs_rg
def test_live_harness_can_fail() -> None:
    r = _rg("-F", "zzz-no-such-string-zzz", "work/axios-get/src/AxiosError.js")
    assert r.returncode == 1 and r.stdout == ""
