"""TS-2 [TOOL] distill kit: plan packets, check gate, gates single path."""
import json
import subprocess
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from book2skill import distill as distill_mod
from book2skill import gates as gates_mod
from book2skill.cli import main

ROOT = Path(__file__).resolve().parent.parent


def _skill(tmp_path: Path, name: str = "demo-distill") -> Path:
    skill = tmp_path / name
    (skill / "references").mkdir(parents=True)
    text = ("---\nname: demo-distill\ndescription: Use when testing the distill gate over rules.\n---\n\n"
            "# Demo\n\n- `do this` (see `0000.txt`)\n")
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    pairs = "".join(
        f"### pair-{n}\n\ngood:\n```\ndo this {n}\n```\nprints: `ok {n}`\n\n"
        for n in range(10)
    )
    (skill / "references" / "pairs.md").write_text("# Pairs\n\n" + pairs, encoding="utf-8")
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("do this: the manual text\n", encoding="utf-8")
    (work / "full_text.txt").write_text("do this: the manual text\n", encoding="utf-8")
    return skill


def test_plan_packets_fit_cap_on_progit() -> None:
    work = ROOT / "work" / "progit-branching"
    if not (work / "chunks").is_dir():
        pytest.skip("work/progit-branching chunks not present")
    plan_file = work / "distill_plan.json"
    try:
        receipt = distill_mod.plan(work)
    finally:
        plan_file.unlink(missing_ok=True)
    assert receipt["chunks"] == len(list((work / "chunks").glob("*.txt")))
    assert receipt["chunks"] > 0
    covered = [c for p in receipt["packets"] for c in p["chunks"]]
    assert sorted(covered) == sorted(p.name for p in (work / "chunks").glob("*.txt"))
    assert all(p["tokens"] <= distill_mod.PACK_TOKENS for p in receipt["packets"])
    assert receipt["prompt"] == "v2"


def test_check_refuses_freud_and_names_scaffold_and_locators() -> None:
    report = distill_mod.check(ROOT / "skills" / "freud-dream-psychology")
    assert report["ok"] is False
    blob = "\n".join(report["findings"])
    assert "scaffold" in blob
    assert "locator" in blob


def test_check_passes_pwsh() -> None:
    report = distill_mod.check(ROOT / "skills" / "pwsh-for-bash-writers")
    assert report["ok"] is True, report["findings"]
    assert report["pairs_total"] >= 10


def test_check_fixture_passes_with_work_locators(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    report = distill_mod.check(skill, tmp_path / "work")
    assert report["ok"] is True, report["findings"]
    assert report["locators"]["chunk_refs"] == 1


def test_check_flags_dangling_chunk_ref(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    text = (skill / "SKILL.md").read_text(encoding="utf-8").replace("0000.txt", "9999.txt")
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    report = distill_mod.check(skill, tmp_path / "work")
    assert report["ok"] is False
    assert any("locator" in f and "9999.txt" in f for f in report["findings"])


def test_gates_live_in_book2skill_gates_single_path() -> None:
    import skill_gates as shim

    assert shim.check_format is gates_mod.check_format
    assert shim.check_sources is gates_mod.check_sources
    assert shim.check_eval is gates_mod.check_eval
    assert shim.fingerprint is gates_mod.fingerprint
    assert shim.FLEET_SKILLS is gates_mod.FLEET_SKILLS


def test_cli_distill_check_exit_codes() -> None:
    runner = CliRunner()
    bad = runner.invoke(main, ["distill", "check", "--skill", "skills/freud-dream-psychology"])
    assert bad.exit_code == 1
    assert "scaffold" in bad.output and "locator" in bad.output
    good = runner.invoke(main, ["distill", "check", "--skill", "skills/pwsh-for-bash-writers"])
    assert good.exit_code == 0, good.output


def test_skill_lint_cli_exit_codes() -> None:
    lint = str(ROOT / "tools" / "skill_lint.py")
    bad = subprocess.run([sys.executable, lint, "check", "--skill", "skills/freud-dream-psychology"],
                         capture_output=True, text=True, cwd=ROOT)
    assert bad.returncode == 1
    assert "scaffold" in bad.stdout and "locator" in bad.stdout
    good = subprocess.run([sys.executable, lint, "check", "--skill", "skills/pwsh-for-bash-writers"],
                          capture_output=True, text=True, cwd=ROOT)
    assert good.returncode == 0
    assert "RESULT PASS" in good.stdout
