"""pwsh-for-bash-writers: the examples in the skill really behave as written, in pwsh 7 without Git's usr/bin on PATH."""
import importlib.util
import json
import re
import shutil
import subprocess
import sys

import pytest

import skill_gates as g
from skill_gates import live

NAME = "pwsh-for-bash-writers"
SKILL = g.SKILLS / NAME
SCRIPTS = SKILL / "scripts"

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")
needs_pwsh = pytest.mark.skipif(shutil.which("pwsh") is None, reason="pwsh 7 is not installed")


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def doc() -> dict:
    return json.loads((SKILL / "references" / "pairs.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def results(doc: dict) -> dict:
    if shutil.which("pwsh") is None:
        pytest.skip("pwsh 7 is not installed")
    return {r["id"]: r for r in _load("run_pairs").run_pairs(doc)}


def test_pair_file_is_well_formed(doc: dict) -> None:
    ids = [p["id"] for p in doc["pairs"]]
    assert len(ids) == len(set(ids)) >= 40
    for p in doc["pairs"]:
        assert p.get("good"), p["id"]
        assert p.get("expect") or p.get("expect_regex"), p["id"]
        if p.get("bad") is not None:
            assert p.get("bad_silent") or p.get("bad_error"), f"{p['id']}: say how bad fails"


def test_pairs_md_is_current() -> None:
    assert _load("pairs_to_md").main(["--check"]) == 0


@live
@needs_pwsh
def test_every_pair_behaves_as_written(results: dict) -> None:
    bad = {k: v["why"] for k, v in results.items() if not v["skipped"] and (v["bad_ok"] is False or v["good_ok"] is False)}
    assert not bad, bad
    ran = [k for k, v in results.items() if not v["skipped"]]
    assert len(ran) >= 40, f"only {len(ran)} pairs ran, skipped: {[k for k, v in results.items() if v['skipped']]}"


@live
@needs_pwsh
def test_the_harness_can_fail() -> None:
    """A pair whose bad command works, and whose good command prints the wrong thing, must be reported."""
    doc = {
        "fixture": {"notes.txt": "alpha\n"},
        "pairs": [{"id": "liar", "group": "x", "bad": "Get-Content notes.txt", "bad_error": "not recognized",
                   "good": "Get-Content notes.txt", "expect": "NOT THERE"}],
    }
    res = _load("run_pairs").run_pairs(doc)[0]
    assert res["bad_ok"] is False and res["good_ok"] is False


def test_every_table_line_in_skill_md_is_a_tested_pair(doc: dict) -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    lines = re.findall(r"^- `(.+?)` -> `(.+)`$", text, re.M)
    assert len(lines) >= 20
    known = {(p.get("bad"), p["good"]) for p in doc["pairs"]}
    missing = [bad for bad, good in lines if (bad, good) not in known]
    assert not missing, f"SKILL.md shows commands no pair tests: {missing}"


@live
@needs_pwsh
def test_error_fragments_come_from_real_failures(results: dict) -> None:
    text = (SKILL / "references" / "errors.md").read_text(encoding="utf-8")
    rows = re.findall(r"^- `(.+?)`: .*?Pair `([\w-]+)`", text, re.M)
    assert len(rows) >= 14
    for fragment, pair_id in rows:
        got = results[pair_id]["bad_text"]
        assert fragment.lower() in got.lower(), f"errors.md says {fragment!r} for {pair_id}, the real error was {got.strip()[:200]!r}"


@live
@needs_pwsh
def test_only_the_log_redirect_through_cmd_stops_the_hang() -> None:
    """Child lives 7 s. A call that waits for it closes after 7 s or more; the good recipe closes at once."""
    out = subprocess.run(["node", str(SCRIPTS / "hang_demo.mjs"), "7"], capture_output=True, text=True, timeout=120).stdout
    verdict = {letter: word for word, letter in re.findall(r"^(HANGS|ok)\s.*\|\s([A-D])\s", out, re.M)}
    assert verdict == {"A": "HANGS", "B": "HANGS", "C": "HANGS", "D": "ok"}, out
