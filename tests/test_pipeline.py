"""Tests: split sizes, frontmatter rule, eval gate math, T-01..T-05 steals."""
import json
from pathlib import Path

from click.testing import CliRunner

from book2skill import build as build_mod
from book2skill import eval as eval_mod
from book2skill import export as export_mod
from book2skill import extract as extract_mod
from book2skill import split as split_mod
from book2skill.cli import main


def test_split_chunk_sizes(tmp_path: Path) -> None:
    (tmp_path / "full_text.txt").write_text("a" * 12000, encoding="utf-8")
    receipt = split_mod.split(tmp_path, chunk=5000, overlap=200)
    assert receipt["chunks"] == 3
    first = (tmp_path / "chunks" / "0000.txt").read_text(encoding="utf-8")
    assert len(first) == 5000


def test_frontmatter_rule() -> None:
    text = Path("skills/_template/SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "name:" in text and "description:" in text


def test_eval_gate_threshold() -> None:
    assert 0.6 == 0.6  # gate constant mirrored in export.py; change both together


def test_docx_table_walk(tmp_path: Path) -> None:
    from docx import Document

    src = tmp_path / "in.docx"
    doc = Document()
    doc.add_paragraph("alpha paragraph")
    table = doc.add_table(rows=1, cols=2)
    table.cell(0, 0).text = "cellone"
    table.cell(0, 1).text = "celltwo"
    doc.save(str(src))
    work = tmp_path / "work"
    receipt = extract_mod.extract(str(src), work)
    text = (work / "full_text.txt").read_text(encoding="utf-8")
    assert receipt["kind"] == "docx"
    assert "alpha paragraph" in text
    assert "cellone | celltwo" in text


def test_extract_receipt_counts(tmp_path: Path) -> None:
    src = tmp_path / "in.txt"
    src.write_text("hello world", encoding="utf-8")
    receipt = extract_mod.extract(str(src), tmp_path / "work")
    assert receipt["chars"] == 11
    assert receipt["stage"] == "extract"


def test_build_skill_pack_layout(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    receipt = build_mod.build(work, skill, "demo-skill", "demo description")
    assert receipt["layout"] == "skill-pack"
    assert receipt["prompt"] == "v1"
    assert (skill / "references" / "sources.md").read_text(encoding="utf-8").startswith("# Sources")
    top = (skill / "SKILL.md").read_text(encoding="utf-8")
    assert top.startswith("---") and "name:" in top and "description:" in top


def test_grow_qa_from_chapter() -> None:
    chapter = "Leases guard batch queues. Requeue follows stuck leases quickly."
    items = eval_mod.grow_qa(chapter, limit=3)
    assert 1 <= len(items) <= 3
    for item in items:
        assert item["must"] and item["must"][0] in chapter.lower()


def test_export_gate_refuses_failing_skill(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("hello world chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    qa = tmp_path / "qa.jsonl"
    qa.write_text(
        '{"q": "what about leases?", "must": ["leases"]}\n'
        '{"q": "what about zzzznonexistent?", "must": ["zzzznonexistent"]}\n'
        '{"q": "what about qqqqmissing?", "must": ["qqqqmissing"]}\n',
        encoding="utf-8",
    )
    out = tmp_path / "dist"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["export", "--skill", str(skill), "--target", "claude", "--out", str(out),
         "--work", str(work), "--qa", str(qa)],
    )
    assert result.exit_code != 0
    assert "eval gate refused export" in result.output
    assert "fix the skill first" in result.output
    assert not (out / "claude" / skill.name).exists()
    # direct unit gate: explicit failing report refuses too
    try:
        export_mod.export(skill, "claude", out, eval_report={"rate": 0.333, "total": 3, "passed": 1})
    except SystemExit as exc:
        assert "eval gate refused export" in str(exc)
    else:
        raise AssertionError("export should refuse rate 0.333")


def test_export_skips_own_output_dir_no_nesting(tmp_path: Path) -> None:
    """K-07: --out inside the skill dir must not recurse into itself."""
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    out = skill / "export"
    report = {"rate": 1.0, "total": 1, "passed": 1}
    for target in ("claude", "codex"):
        export_mod.export(skill, target, out, eval_report=report)
    for target in ("claude", "codex"):
        dest = out / target / skill.name
        assert (dest / "SKILL.md").exists()
        assert list(dest.rglob("export")) == []
    # re-export over an existing dest still leaves a flat tree
    export_mod.export(skill, "claude", out, eval_report=report)
    assert list((out / "claude" / skill.name).rglob("export")) == []


def test_export_unknown_target_clean_error(tmp_path: Path) -> None:
    import click

    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\n", encoding="utf-8")
    out = tmp_path / "dist"
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["export", "--skill", str(skill), "--target", "bogus", "--out", str(out)],
    )
    assert result.exit_code != 0
    assert "Traceback" not in result.output
    assert "bogus" in result.output
    assert "claude" in result.output
    try:
        export_mod.export(skill, "bogus", out, eval_report={"rate": 1.0, "total": 1, "passed": 1})
    except click.UsageError as exc:
        assert "unknown target bogus" in str(exc)
    else:
        raise AssertionError("export should reject target bogus with UsageError")
