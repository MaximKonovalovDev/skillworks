"""Layer 8 [TOOL] distill plan/check pins packet cap and locator gate."""
from pathlib import Path

from book2skill import distill as distill_mod

NL = chr(10)


def _work(tmp_path: Path) -> Path:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("do this: the manual text" + NL, encoding="utf-8")
    (work / "chunks" / "0001.txt").write_text("do that: more manual text" + NL, encoding="utf-8")
    return work


def _skill(tmp_path: Path, work: Path) -> Path:
    skill = tmp_path / "demo-distill-tool"
    (skill / "references").mkdir(parents=True)
    text = "---" + NL + "name: demo-distill-tool" + NL + "description: Use when testing the distill tool gate." + NL + "---" + NL + NL + "# Demo Tool" + NL + NL + "- `do this` (see `0000.txt`)" + NL
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    pairs = "".join("### pair-" + str(n) + NL + NL + "good:" + NL + "```" + NL + "do this " + str(n) + NL + "```" + NL + "prints: `ok " + str(n) + "`" + NL + NL for n in range(10))
    (skill / "references" / "pairs.md").write_text("# Pairs" + NL + NL + pairs, encoding="utf-8")
    return skill


def test_plan_groups_chunks_within_cap(tmp_path: Path) -> None:
    work = _work(tmp_path)
    receipt = distill_mod.plan(work)
    assert receipt["stage"] == "distill-plan"
    assert receipt["chunks"] == 2
    assert all(p["tokens"] <= distill_mod.PACK_TOKENS for p in receipt["packets"])
    assert (work / "distill_plan.json").is_file()


def test_check_passes_then_flags_dangling(tmp_path: Path) -> None:
    work = _work(tmp_path)
    skill = _skill(tmp_path, work)
    report = distill_mod.check(skill, work)
    assert report["ok"] is True, report["findings"]
    assert report["locators"]["chunk_refs"] == 1
    assert report["pairs_total"] >= 10
    text = (skill / "SKILL.md").read_text(encoding="utf-8").replace("0000.txt", "9999.txt")
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    bad = distill_mod.check(skill, work)
    assert bad["ok"] is False
    assert any("9999.txt" in f and "locator" in f for f in bad["findings"])
