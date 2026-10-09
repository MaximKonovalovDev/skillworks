"""idiomatic-rust: the twelve rules, the files they name, and the 12 pairs really run.

Offline tests (default run): pairs.json shape, pairs.md freshness, every
SKILL.md rule line carrying its src anchor, every trial and QA must word
literally present in the skill text, the ISBN pin, the token budget.
Live tests (SKILL_LIVE=1): all 12 pairs through scripts/idiomatic_rust.py,
the harness can fail probe, and an installed copy driven through python.
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

NAME = "idiomatic-rust"
SKILL = g.SKILLS / NAME
SCRIPTS = SKILL / "scripts"
PAIRS = SKILL / "references" / "pairs.json"
PIN = "9781633437463"

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")


def _load(name: str):
    spec = importlib.util.spec_from_file_location("idiomatic_rust_" + name, SCRIPTS / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["idiomatic_rust_" + name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def doc() -> dict:
    return json.loads(PAIRS.read_text(encoding="utf-8"))


def test_pair_file_is_well_formed(doc: dict) -> None:
    ids = [p["id"] for p in doc["pairs"]]
    assert len(ids) == len(set(ids)) >= 12
    for p in doc["pairs"]:
        assert p.get("bad_code") and p.get("good_code"), p["id"]
        assert p.get("expect") and p.get("bad_error"), p["id"]


def test_pairs_md_is_current() -> None:
    assert _load("pairs_to_md").main(["--check"]) == 0


def test_pairs_md_covers_every_pair(doc: dict) -> None:
    text = (SKILL / "references" / "pairs.md").read_text(encoding="utf-8")
    for p in doc["pairs"]:
        assert "### " + p["id"] in text, p["id"]
    assert text.count("prints:") >= 12


def test_every_rule_line_carries_a_source(doc: dict) -> None:
    ids = {p["id"] for p in doc["pairs"]}
    body = g.body_of((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    rules = [ln for ln in body.splitlines() if re.match(r"^\s*[-*]\s+.*`[^`]+`.*$", ln)]
    assert len(rules) >= 12, "only " + str(len(rules)) + " rule lines"
    missing = [ln for ln in rules if not ln.rstrip().endswith("]") or "[src:" not in ln]
    assert not missing, "rule lines without trailing src: " + str(missing[:2])
    anchors = set(re.findall(r"references/pairs\.md#(ir-p\d+)", body))
    assert anchors <= ids, "anchors without pair: " + str(sorted(anchors - ids))
    assert len(anchors) >= 12, "only " + str(len(anchors)) + " pair anchors"


def _skill_text() -> str:
    return g.skill_text(NAME).lower()


def test_trial_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for line in (g.ROOT / "evals" / "idiomatic-rust_trials.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row.get("must", []):
            assert m.lower() in text, "must " + repr(m) + " not in skill text (task " + row["id"] + ")"


def test_qa_musts_literally_appear_in_the_skill_text() -> None:
    text = _skill_text()
    for line in (g.ROOT / "evals" / "idiomatic-rust_qa.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        for m in row["must"]:
            assert m.lower() in text, "must " + repr(m) + " not in skill text (question " + row["q"] + ")"


def test_pin_is_the_same_in_every_file() -> None:
    for f in ("references/sources.md", "SKILL.md"):
        t = (SKILL / f).read_text(encoding="utf-8")
        assert PIN in t, f + " must name " + PIN


def test_skill_body_within_budget() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert g.body_tokens(text) <= g.BODY_TOKEN_BUDGET


def test_no_private_paths_in_the_public_skill() -> None:
    for p in SKILL.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".py"}:
            t = p.read_text(encoding="utf-8")
            assert not re.search(r"[A-Za-z]:\\\\Users\\\\|/Users/[a-z]|ghp_|github_pat_", t), p.name + " has private path"


def test_every_pair_behaves_as_written(doc: dict) -> None:
    results = _load("idiomatic_rust").run_pairs(doc)
    bad = {r["id"]: r["why"] for r in results if not r["ok"]}
    assert not bad, bad
    assert len(results) >= 12, "only " + str(len(results)) + " pairs ran"


def test_the_harness_can_fail(doc: dict) -> None:
    mod = _load("idiomatic_rust")
    clean, _ = mod.check_text("const MAX_SIZE: u32 = 10;")
    assert clean is True
    clean2, found = mod.check_text("const max_size: u32 = 10;")
    assert clean2 is False and found, "bad naming must fail"


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPTS / "idiomatic_rust.py", "--check", "--pair", "--json")


def test_an_installed_copy_runs_from_another_folder_through_python(tmp_path: Path) -> None:
    dest = tmp_path / "elsewhere" / "idiomatic_rust.py"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes((SCRIPTS / "idiomatic_rust.py").read_bytes())
    elsewhere = tmp_path / "run-here"
    elsewhere.mkdir()
    r = subprocess.run([sys.executable, str(dest), "--help"], cwd=elsewhere, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 0 and "--check" in r.stdout
    assert not list(elsewhere.iterdir()), "nothing written next to start dir"


@live
def test_live_pairs_through_subprocess(doc: dict) -> None:
    r = stock.run_script(SCRIPTS / "idiomatic_rust.py")
    assert r.returncode == 0 and "12 of 12 pairs behave as written" in r.stdout, r.stdout + r.stderr

