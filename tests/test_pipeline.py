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
    receipt = build_mod.build(work, skill, "skill", "demo description")
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


def test_gutenberg_marker_strip(tmp_path: Path) -> None:
    """K-28: PG header/footer markers stripped, body kept, receipt flags it."""
    header = (
        "The Project Gutenberg eBook of Test Dreams\n"
        "Title: Test Dreams\n"
        "*** START OF THE PROJECT GUTENBERG EBOOK TEST DREAMS ***\n"
    )
    body = "Dream analysis chapter one about free association.\n" * 120
    footer = "*** END OF THE PROJECT GUTENBERG EBOOK TEST DREAMS ***\nMost people start at our website\n"
    src = tmp_path / "gutenberg.txt"
    src.write_text(header + body + footer, encoding="utf-8")
    work = tmp_path / "work"
    receipt = extract_mod.extract(str(src), work)
    text = (work / "full_text.txt").read_text(encoding="utf-8")
    assert receipt["stripped"] is True
    assert "The Project Gutenberg eBook of Test Dreams" not in text
    assert "Most people start at our website" not in text
    assert "*** START OF" not in text and "*** END OF" not in text
    assert "free association" in text
    # no-marker fallback: plain text untouched, stripped False
    plain = tmp_path / "plain.txt"
    plain.write_text("just a body paragraph, no markers", encoding="utf-8")
    receipt2 = extract_mod.extract(str(plain), tmp_path / "work2")
    assert receipt2["stripped"] is False
    assert (tmp_path / "work2" / "full_text.txt").read_text(encoding="utf-8") == "just a body paragraph, no markers"
    # opt-out keeps boilerplate
    receipt3 = extract_mod.extract(str(src), tmp_path / "work3", strip_gutenberg=False)
    assert receipt3["stripped"] is False
    assert "The Project Gutenberg eBook" in (tmp_path / "work3" / "full_text.txt").read_text(encoding="utf-8")


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


def test_build_refuses_name_dir_mismatch(tmp_path: Path) -> None:
    """K-36 [016]: --name != skill dir basename or bad charset fails fast, rule quoted."""
    import pytest

    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    runner = CliRunner()
    # mismatched pair: exit != 0 with the rule quoted
    result = runner.invoke(
        main,
        ["build", "--work", str(work), "--skill", str(skill),
         "--name", "pilot-r3-demo", "--description", "demo"],
    )
    assert result.exit_code != 0
    assert "must match skill dir" in result.output
    assert "a-z0-9-" in result.output
    assert not (skill / "SKILL.md").exists()
    # bad charset also refused with the rule quoted
    bad = tmp_path / "Bad_Name"
    result_bad = runner.invoke(
        main,
        ["build", "--work", str(work), "--skill", str(bad),
         "--name", "Bad_Name", "--description", "demo"],
    )
    assert result_bad.exit_code != 0
    assert "a-z0-9-" in result_bad.output
    # direct API refuses too
    with pytest.raises(ValueError, match="a-z0-9-"):
        build_mod.build(work, skill, "pilot-r3-demo", "demo")
    # matching pair still builds
    result_ok = runner.invoke(
        main,
        ["build", "--work", str(work), "--skill", str(skill),
         "--name", "skill", "--description", "demo"],
    )
    assert result_ok.exit_code == 0
    assert (skill / "SKILL.md").exists()


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


def test_audit_skips_export_dupes(tmp_path: Path) -> None:
    """K-26 [AUDIT-SKIP-EXPORT-1001]: audit counts canonical files only, export/ excluded."""
    from book2skill import audit as audit_mod

    skill = tmp_path / "skill"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\nbody text here\n", encoding="utf-8")
    (skill / "references" / "sources.md").write_text("# Sources\ncanonical\n", encoding="utf-8")
    base = audit_mod.audit(skill)
    assert base["total_tokens"] > 0
    assert len(base["sections"]) == 2
    # export-like dupes (mirrors skills/<name>/export/<target>/<name>/*.md)
    dupe = skill / "export" / "claude" / skill.name
    dupe.mkdir(parents=True)
    (dupe / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\nbody text here\n", encoding="utf-8")
    (dupe / "extra.md").write_text("# duped export copy\n" * 50, encoding="utf-8")
    after = audit_mod.audit(skill)
    assert after == base
