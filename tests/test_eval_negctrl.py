"""STEAL S negative control: keyword-stuffed-but-empty skill must fail the gate.

A gutted SKILL.md that lists every query and must keyword (so the old
substring grade alone would pass) still scores below the 0.6 export gate
because the deterministic substance check is ANDed with the substring
grade. A genuine skill with real sentences still passes.
"""
from pathlib import Path

from book2skill import eval as eval_mod

QA = (
    "{\"q\": \"what does the chapter say about leases?\", \"must\": [\"leases\"]}\n"
    "{\"q\": \"how are renewals handled?\", \"must\": [\"renewals\"]}\n"
)

def _work(root: Path) -> Path:
    work = root / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text(
        "chapter about leases and how renewals are handled", encoding="utf-8")
    return work

def _stuffed_skill(root: Path) -> Path:
    skill = root / "skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when demoing.\n---\n"
        "leases what chapter say about\n"
        "renewals how handled\n"
        "leases what chapter say about renewals how handled\n",
        encoding="utf-8")
    return skill

def _real_skill(root: Path) -> Path:
    skill = root / "skill"
    (skill / "chapters").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when handling leases.\n---\n"
        "# demo\n\nThis skill is about leases.\n", encoding="utf-8")
    (skill / "chapters" / "notes.md").write_text(
        "Leases renew yearly; renewals need a signature.\n", encoding="utf-8")
    return skill

def _qa(root: Path) -> Path:
    qa = root / "qa.jsonl"
    qa.write_text(QA, encoding="utf-8")
    return qa

def test_stuffed_but_empty_skill_scores_below_gate(tmp_path: Path) -> None:
    report = eval_mod.run_eval(_work(tmp_path), _stuffed_skill(tmp_path), _qa(tmp_path))
    assert report["graded_on"] == "skill"
    assert report["rate"] < 0.6

def test_real_skill_still_passes(tmp_path: Path) -> None:
    report = eval_mod.run_eval(_work(tmp_path), _real_skill(tmp_path), _qa(tmp_path))
    assert report["rate"] == 1.0
