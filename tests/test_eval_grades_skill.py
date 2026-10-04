"""K-48 slice (4): eval grades what the SKILL answers, not its source chunks.

A QA pair passes only when the skill's own text (SKILL.md + references
answers) produces the answer. A gutted skill fails even when the work chunks
still hold every answer; the export gate (rate < 0.6 refuses) is untouched.
"""
import json
from pathlib import Path

import pytest

from book2skill import eval as eval_mod
from book2skill import export as export_mod

QA = (
    '{"q": "what does the chapter say about leases?", "must": ["leases"]}\n'
    '{"q": "how are renewals handled?", "must": ["renewals"]}\n'
)


def _work_with_answers(root: Path) -> Path:
    work = root / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text(
        "chapter about leases and how renewals are handled", encoding="utf-8")
    return work


def _skill_with_answers(root: Path) -> Path:
    skill = root / "skill"
    (skill / "chapters").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when handling leases.\n---\n"
        "# demo\n\nThis skill is about leases.\n", encoding="utf-8")
    (skill / "chapters" / "notes.md").write_text(
        "Leases renew yearly; renewals need a signature.\n", encoding="utf-8")
    (skill / "glossary.md").write_text("# Glossary\n\nleases, renewals.\n", encoding="utf-8")
    (skill / "references").mkdir(exist_ok=True)
    (skill / "references" / "sources.md").write_text("# Sources\n\nowned.\n", encoding="utf-8")
    # Shop copy must never grade a pair: it holds the answers too, on purpose.
    (skill / "listing.md").write_text("PREP-ONLY leases renewals\n", encoding="utf-8")
    (skill / "demo").mkdir(exist_ok=True)
    (skill / "demo" / "demo.gif").write_bytes(b"GIF89a")
    return skill


def _qa(root: Path) -> Path:
    qa = root / "qa.jsonl"
    qa.write_text(QA, encoding="utf-8")
    return qa


def test_eval_passes_when_the_skill_answers(tmp_path: Path) -> None:
    report = eval_mod.run_eval(_work_with_answers(tmp_path), _skill_with_answers(tmp_path), _qa(tmp_path))
    assert (report["total"], report["passed"], report["rate"]) == (2, 2, 1.0)
    assert report["graded_on"] == "skill"


def test_eval_fails_when_the_skill_is_gutted_but_chunks_answer(tmp_path: Path) -> None:
    """F2P core: the old eval read work chunks, so a broken skill still passed."""
    work = _work_with_answers(tmp_path)
    skill = _skill_with_answers(tmp_path)
    qa = _qa(tmp_path)
    assert eval_mod.run_eval(work, skill, qa)["rate"] == 1.0
    # Gut the skill the way a broken scaffold looks: files present, answers gone.
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when handling leases.\n---\nempty.\n", encoding="utf-8")
    (skill / "chapters" / "notes.md").write_text("nothing here yet.\n", encoding="utf-8")
    (skill / "glossary.md").write_text("# Glossary\n\nFill terms while reading.\n", encoding="utf-8")
    (skill / "listing.md").write_text("PREP-ONLY\n", encoding="utf-8")
    report = eval_mod.run_eval(work, skill, qa)
    assert report["graded_on"] == "skill"
    assert report["rate"] == 0.0
    with pytest.raises(SystemExit, match="eval gate refused export"):
        export_mod.export(skill, "claude", tmp_path / "dist")


def test_skill_text_beats_shop_copy_and_missing_files(tmp_path: Path) -> None:
    """Only answer files grade: listing/demo/report/lock text never passes a pair."""
    work = _work_with_answers(tmp_path)
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    (skill / "listing.md").write_text("leases renewals for sale\n", encoding="utf-8")
    (skill / "eval_report.json").write_text(json.dumps({"rate": 1.0}), encoding="utf-8")
    report = eval_mod.run_eval(work, skill, _qa(tmp_path))
    assert report["rate"] == 0.0


def test_gate_arithmetic_untouched(tmp_path: Path) -> None:
    """rate < 0.6 refuses export; 0.6 ships. The gate number never moved."""
    assert export_mod.GATE == 0.6
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="rate 0.599 below 0.6"):
        export_mod.export(skill, "claude", tmp_path / "dist",
                          eval_report={"rate": 0.599, "total": 5, "passed": 3})
    receipt = export_mod.export(skill, "claude", tmp_path / "dist",
                                eval_report={"rate": 0.6, "total": 5, "passed": 3})
    assert (tmp_path / "dist" / "claude" / "skill").is_dir()
    assert receipt["dest"].endswith("skill")
