"""O-013: one redacted rubric sample lands, eval keeps 0.6 or more.

Own words only: no DataAnnotation/Prolific task text in git, AI-use ban
honored. Shape copies tests/test_eval_grades_skill.py (tmp skill + run_eval)
plus the gate number check (export GATE 0.6).
"""
from pathlib import Path

from book2skill import eval as eval_mod
from book2skill import export as export_mod

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "evals" / "human-rubric-sample.md"


def test_rubric_sample_is_redacted_own_words() -> None:
    text = SAMPLE.read_text(encoding="utf-8")
    assert "REDACTED" in text and "own words" in text
    assert "AI-use ban" in text
    assert "No vendor task text in git" in text
    for criterion in ("Correct", "Whole", "Clear", "Safe", "Shaped"):
        assert criterion in text


def test_rubric_sample_carries_grade_delta_above_gate() -> None:
    text = SAMPLE.read_text(encoding="utf-8")
    assert "rate 1.0" in text
    assert "0.6 or more" in text
    assert "RESULT PASS" in text


def test_eval_gate_untouched_and_demo_skill_passes(tmp_path: Path) -> None:
    assert export_mod.GATE == 0.6
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("leases and renewals note", encoding="utf-8")
    skill = tmp_path / "skill"
    (skill / "chapters").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when handling leases.\n---\n"
        "# demo\n\nThis skill is about leases and renewals.\n", encoding="utf-8")
    (skill / "chapters" / "notes.md").write_text(
        "Leases renew yearly; renewals need a signature.\n", encoding="utf-8")
    qa = tmp_path / "qa.jsonl"
    qa.write_text(
        '{"q": "what does the chapter say about leases?", "must": ["leases"]}\n'
        '{"q": "how are renewals handled?", "must": ["renewals"]}\n',
        encoding="utf-8")
    report = eval_mod.run_eval(work, skill, qa)
    assert report["rate"] >= 0.6
