"""012-report-persist: eval saves eval_report.json beside the skill."""
import json
from pathlib import Path

from click.testing import CliRunner

from book2skill import eval as eval_mod
from book2skill.cli import main


def test_eval_persists_report_beside_skill(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("hello world chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    skill.mkdir()
    qa = tmp_path / "qa.jsonl"
    qa.write_text('{"q": "what about leases?", "must": ["leases"]}\n', encoding="utf-8")
    report = eval_mod.run_eval(work, skill, qa)
    saved = json.loads((skill / "eval_report.json").read_text(encoding="utf-8"))
    assert saved == report
    assert saved["rate"] == 1.0


def test_readme_order_eval_then_export(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("hello world chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\nAbout leases: renew yearly.\n", encoding="utf-8")
    qa = tmp_path / "qa.jsonl"
    qa.write_text('{"q": "what about leases?", "must": ["leases"]}\n', encoding="utf-8")
    out = tmp_path / "dist"
    runner = CliRunner()
    r1 = runner.invoke(
        main,
        ["eval", "--work", str(work), "--skill", str(skill), "--qa", str(qa)],
    )
    assert r1.exit_code == 0
    assert (skill / "eval_report.json").exists()
    r2 = runner.invoke(
        main,
        ["export", "--skill", str(skill), "--target", "claude", "--out", str(out)],
    )
    assert r2.exit_code == 0, r2.output
    assert (out / "claude" / skill.name).exists()
