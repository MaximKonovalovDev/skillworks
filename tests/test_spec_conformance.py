"""SK-08: spec conformance plus Gutenberg normalize.

Today no tool checks one SKILL.md against the spec bar (frontmatter,
chapters, eval report beside the skill), and no normalize step strips
PG markers plus metadata layout. After the fix: tools/spec_conformance.py
gates one skill dir, tools/gutenberg_normalize.py cleans one text with a
byte-identical plain-note path.
"""
from pathlib import Path

from tools import gutenberg_normalize as gn
from tools import spec_conformance as sc

DESC = ("Freud dream notes: condensation and displacement. "
        "Use when analyzing dreams or discussing interpretation.")


def _skill(root: Path, name: str = "demo-skill", desc: str = DESC) -> Path:
    skill = root / name
    (skill / "chapters").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {desc}\nlicense: MIT\n---\n\n# {name}\n\nBody.\n",
        encoding="utf-8",
    )
    (skill / "chapters" / "notes.md").write_text("# Notes\n\nBody notes.\n", encoding="utf-8")
    (skill / "eval_report.json").write_text(
        '{"total": 12, "passed": 10, "rate": 0.833}', encoding="utf-8"
    )
    return skill


def test_valid_skill_passes(tmp_path: Path) -> None:
    report = sc.check(_skill(tmp_path))
    assert report["ok"], report["findings"]


def test_bad_name_and_short_description_fail(tmp_path: Path) -> None:
    skill = _skill(tmp_path, desc="Too short.")
    (skill / "SKILL.md").write_text(
        "---\nname: wrong\ndescription: Too short.\nlicense: MIT\n---\nBody.\n",
        encoding="utf-8",
    )
    report = sc.check(skill)
    assert not report["ok"]
    text = " ".join(w for _, w in report["findings"])
    assert "must equal the folder" in text and "description" in text


def test_missing_chapters_and_eval_fail(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    (skill / "chapters" / "notes.md").unlink()
    (skill / "chapters").rmdir()
    (skill / "eval_report.json").unlink()
    report = sc.check(skill, evals_dir=tmp_path / "no-evals")
    assert not report["ok"]
    text = " ".join(w for _, w in report["findings"])
    assert "chapters" in text and "eval report" in text


def test_missing_named_file_fails(tmp_path: Path) -> None:
    skill = _skill(tmp_path)
    (skill / "SKILL.md").write_text(
        (skill / "SKILL.md").read_text(encoding="utf-8") + "\nSee `references/deep.md`.\n",
        encoding="utf-8",
    )
    report = sc.check(skill)
    assert not report["ok"]


def test_normalize_strips_markers() -> None:
    body = "Real body line about dreams.\n" * 120
    raw = ("Title: Test Dreams\nAuthor: Test Author\n\n"
           + "*** START OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
           + body
           + "*** END OF THE PROJECT GUTENBERG EBOOK TEST ***\n"
           + "Most people start at our website\n")
    out, fired = gn.normalize(raw)
    assert fired is True
    assert "Real body line about dreams" in out
    assert "Gutenberg" not in out and "Most people start" not in out


def test_normalize_strips_metadata_layout() -> None:
    head = "Title: Test Dreams\nAuthor: Test Author\nRelease Date: Jan 1\n\n"
    raw = head + "Real body line.\n" * 3
    out, fired = gn.normalize(raw)
    assert fired is True
    assert "Real body line" in out
    assert "Title:" not in out and "Author:" not in out


def test_normalize_plain_note_byte_identical(tmp_path: Path) -> None:
    raw = b"chapter about leases\nsecond line\n"
    src = tmp_path / "in.txt"
    dst = tmp_path / "out.txt"
    src.write_bytes(raw)
    out, fired = gn.normalize_bytes(raw)
    assert fired is False and out == raw
    assert gn.normalize(raw.decode())[0] == raw.decode()
    rc = gn.main(["--in", str(src), "--out", str(dst)])
    assert rc == 0
    assert dst.read_bytes() == raw
