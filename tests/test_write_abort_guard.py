"""write-abort-guard: the slice-small pairs really behave as written, in pwsh 7 in scratch dirs."""
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

NAME = "write-abort-guard"
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
    return {r["id"]: r for r in _load("run_write").run_pairs(doc)}


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
        "fixture": {"big.txt": "line 01 write chunk slice\n"},
        "pairs": [{"id": "liar", "group": "x", "bad": "'all done'", "bad_error": "Tool execution aborted",
                   "good": "'all done'", "expect": "NOT THERE"}],
    }
    res = _load("run_write").run_pairs(doc)[0]
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
