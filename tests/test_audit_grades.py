"""K-43 [STEAL-AUDIT] graded audit: three cost numbers + gates in book2skill/audit.py."""
import json
from pathlib import Path

from click.testing import CliRunner

from book2skill import audit as audit_mod
from book2skill.cli import main

ROOT = Path(__file__).resolve().parent.parent


def _skill(tmp_path: Path, name: str = "demo-skill", body_chars: int = 200,
           description: str = "Use when chaining commands in PowerShell for testing audits.",
           broken: bool = False) -> Path:
    skill = tmp_path / name
    (skill / "references").mkdir(parents=True)
    body = "x " * (body_chars // 2)
    text = (f"---\nname: {name}\ndescription: {description}\n---\n{body}\n"
            + ("[gone](missing.md)\n" if broken else ""))
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    (skill / "references" / "sources.md").write_text("# Sources\n\n- `0000.txt`\n", encoding="utf-8")
    return skill


def test_audit_reports_three_cost_numbers_on_progit() -> None:
    report = audit_mod.audit(ROOT / "skills" / "progit-branching")
    assert report["always_loaded_tokens"] > 0
    assert report["body_tokens"] > 0
    assert report["references_tokens"] >= 0
    assert report["total_tokens"] == sum(s["tokens"] for s in report["sections"])
    assert report["body_budget"] == 2000


def test_audit_flags_an_over_budget_body(tmp_path: Path) -> None:
    skill = _skill(tmp_path, body_chars=12000)
    report = audit_mod.audit(skill)
    assert report["body_tokens"] > 2000
    assert report["over_budget"] is True
    assert any("over budget" in f for f in report["flags"])
    small = _skill(tmp_path, name="tiny-skill", body_chars=200)
    quiet = audit_mod.audit(small)
    assert quiet["over_budget"] is False


def test_audit_grades_description_name_and_links(tmp_path: Path) -> None:
    bad = _skill(tmp_path, name="demo-skill", description="short",
                 body_chars=200, broken=True)
    report = audit_mod.audit(bad)
    assert report["description"]["ok"] is False
    assert any("trigger" in r for r in report["description"]["reasons"])
    assert report["broken_links"] and report["broken_links"][0]["target"] == "missing.md"
    assert any("broken links" in f for f in report["flags"])
    # name/dir mismatch is flagged
    (bad / "SKILL.md").write_text(
        "---\nname: other-name\ndescription: Use when testing the name dir gate with enough chars here.\n---\nbody\n",
        encoding="utf-8")
    again = audit_mod.audit(bad)
    assert again["name_check"]["ok"] is False
    good = _skill(tmp_path, name="good-skill")
    ok = audit_mod.audit(good)
    assert ok["description"]["ok"] is True and ok["name_check"]["ok"] is True
    assert ok["broken_links"] == []


def test_audit_reads_folded_yaml_description(tmp_path: Path) -> None:
    """O-008: a `description: >-` folded scalar must not read as 2 chars."""
    skill = tmp_path / "folded-skill"
    (skill / "references").mkdir(parents=True)
    folded = ("Use when chaining commands in PowerShell for testing folded audits "
              "with enough characters to clear the length gate.")
    assert len(folded) >= audit_mod.DESC_MIN
    (skill / "SKILL.md").write_text(
        f"---\nname: folded-skill\ndescription: >-\n  {folded}\n---\nbody text here\n",
        encoding="utf-8")
    report = audit_mod.audit(skill)
    assert report["description"]["chars"] == len(folded)
    assert report["description"]["ok"] is True
    assert not any("2 chars" in f for f in report["flags"])
    # Literal block style reads in full too.
    literal = tmp_path / "literal-skill"
    (literal / "references").mkdir(parents=True)
    (literal / "SKILL.md").write_text(
        "---\nname: literal-skill\ndescription: |\n  Use when testing literal blocks with enough chars here.\n---\nbody\n",
        encoding="utf-8")
    lit_report = audit_mod.audit(literal)
    assert lit_report["description"]["chars"] > 40
    assert lit_report["description"]["ok"] is True


def test_audit_git_one_branch_has_no_folded_length_flag() -> None:
    """O-008 regression on the shipped skill: no `2 chars` length misread."""
    report = audit_mod.audit(ROOT / "skills" / "git-one-branch")
    assert report["description"]["chars"] > 40
    assert not any("2 chars" in f for f in report["flags"])
    assert not any("chars, want" in r for r in report["description"]["reasons"])


def test_make_prints_over_budget_on_a_big_fixture(tmp_path: Path) -> None:
    docs = tmp_path / "manual"
    docs.mkdir()
    (docs / "big.md").write_text("# Big\n\n" + ("word " * 100000), encoding="utf-8")
    qa = tmp_path / "qa.jsonl"
    qa.write_text('{"q": "what is the word", "must": ["word"]}\n', encoding="utf-8")
    work = tmp_path / "work" / "big-skill"
    skill = tmp_path / "skills" / "big-skill"
    result = CliRunner().invoke(main, ["make", "--in", str(docs), "--name", "big-skill",
                                      "--description", "Use when testing a big skill over budget here.",
                                      "--qa", str(qa), "--work", str(work), "--skill", str(skill)])
    assert result.exit_code == 0, result.output
    assert "over budget" in result.output
    made = json.loads((work / "make.json").read_text(encoding="utf-8"))
    assert made["stages"]["audit"]["over_budget"] is True
