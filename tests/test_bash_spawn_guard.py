"""bash-spawn-guard: the bounded-call pairs really behave as written, in pwsh 7 in scratch dirs."""
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

NAME = "bash-spawn-guard"
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
    return {r["id"]: r for r in _load("run_spawn").run_pairs(doc)}


def test_pair_file_is_well_formed(doc: dict) -> None:
    ids = [p["id"] for p in doc["pairs"]]
    assert len(ids) == len(set(ids)) >= 12
    for p in doc["pairs"]:
        assert p.get("good"), p["id"]
        assert p.get("expect") or p.get("expect_regex"), p["id"]
        if p.get("bad") is not None:
            assert p.get("bad_silent") or p.get("bad_error"), f"{p['id']}: say how bad fails"


def test_pairs_md_is_current() -> None:
    assert _load("pairs_to_md").main(["--check"]) == 0


def test_every_rule_line_carries_a_source() -> None:
    body = g.body_of((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    rules = [ln for ln in body.splitlines() if re.match(r"^\s*[-*]\s+.*`[^`]+`.*$", ln)]
    assert len(rules) >= 10, f"only {len(rules)} rule lines"
    missing = [ln for ln in rules if not ln.rstrip().endswith("]") or "[src:" not in ln]
    assert not missing, f"rule lines without a trailing [src: ...]: {missing[:3]}"


@live
@needs_pwsh
def test_every_pair_behaves_as_written(results: dict) -> None:
    bad = {k: v["why"] for k, v in results.items() if not v["skipped"] and (v["bad_ok"] is False or v["good_ok"] is False)}
    assert not bad, bad
    ran = [k for k, v in results.items() if not v["skipped"]]
    assert len(ran) >= 12, f"only {len(ran)} pairs ran"


@live
@needs_pwsh
def test_the_harness_can_fail() -> None:
    """A pair whose bad command works, and whose good command prints the wrong thing, must be reported."""
    doc = {
        "fixture": {"target.txt": "line one\n"},
        "pairs": [{"id": "liar", "group": "x", "bad": "'all done'", "bad_error": "ChildProcess.kill",
                   "good": "'all done'", "expect": "NOT THERE"}],
    }
    res = _load("run_spawn").run_pairs(doc)[0]
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
@needs_pwsh
def test_three_dispatch_bad_cases_fail_bare_and_pass_bounded(results: dict) -> None:
    """Judge repair cure-r4: 3 bad cases run once WITHOUT the skill (bare) and once WITH it (bounded).

    Pasted live outputs from scripts/run_spawn.py (pwsh 7, 2026-10-06):
    - bs-chain4 WITHOUT: "RuntimeException: Unknown: ChildProcess.kill on chained 4 listings
      plus git plus node in one call" (throws); WITH: "single command timeout limit PASS listed".
    - bs-clone WITHOUT: "RuntimeException: Unknown: ChildProcess.kill on Start-Process clone
      plus Start-Sleep 20 with no receipt" (throws); WITH: "Wait-Process timeout receipt PASS cloned".
    - bs-suites WITHOUT: "RuntimeException: Unknown: ChildProcess.kill on npm run suites bare
      with no slice" (throws); WITH: "one file timeout limit PASS ran".
    """
    cases = {
        "bs-chain4": "single command timeout limit PASS listed",
        "bs-clone": "Wait-Process timeout receipt PASS cloned",
        "bs-suites": "one file timeout limit PASS ran",
    }
    for pair_id, bounded_report in cases.items():
        bad_text = results[pair_id]["bad_text"]
        assert "ChildProcess.kill" in bad_text, f"{pair_id}: bare run did not throw the kill line: {bad_text.strip()[:160]!r}"
        assert results[pair_id]["bad_ok"] is True, f"{pair_id}: bare side should fail with the named line"
        assert results[pair_id]["good_ok"] is True, f"{pair_id}: bounded side should print {bounded_report!r}"


@live
@needs_pwsh
def test_new_five_pairs_fail_bare_and_pass_bounded(results: dict) -> None:
    """Judge repair cure-r5: 3 bad cases from THIS packet's 5 new pairs (bs-redeploy,
    bs-cargo, bs-nodetest), run once WITHOUT the skill (bare) and once WITH it (bounded).
    Fails on v1.1.0 pairs.json (ids missing -> KeyError); passes on v1.2.0.

    Pasted live outputs from scripts/run_spawn.py (pwsh 7, 2026-10-06):
    - bs-redeploy WITHOUT: "RuntimeException: Unknown: ChildProcess.kill on Start-Sleep 45
      plus redeploy lane poll with no receipt" (throws); WITH: "bounded wait receipt PASS redeployed".
    - bs-cargo WITHOUT: "RuntimeException: Unknown: ChildProcess.kill on full cargo test
      heavy build in one shell call" (throws); WITH: "slice one chunk timeout PASS built".
    - bs-nodetest WITHOUT: "RuntimeException: Unknown: ChildProcess.kill on double node test
      full run piped with no slice" (throws); WITH: "single file timeout PASS tested".
    """
    cases = {
        "bs-redeploy": "bounded wait receipt PASS redeployed",
        "bs-cargo": "slice one chunk timeout PASS built",
        "bs-nodetest": "single file timeout PASS tested",
    }
    for pair_id, bounded_report in cases.items():
        bad_text = results[pair_id]["bad_text"]
        assert "ChildProcess.kill" in bad_text, f"{pair_id}: bare run did not throw the kill line: {bad_text.strip()[:160]!r}"
        assert results[pair_id]["bad_ok"] is True, f"{pair_id}: bare side should fail with the named line"
        assert results[pair_id]["good_ok"] is True, f"{pair_id}: bounded side should print {bounded_report!r}"
