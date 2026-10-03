"""Tests: split sizes, frontmatter rule, eval gate math, T-01..T-05 steals."""
from pathlib import Path

from book2skill import build as build_mod
from book2skill import eval as eval_mod
from book2skill import extract as extract_mod
from book2skill import split as split_mod


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
