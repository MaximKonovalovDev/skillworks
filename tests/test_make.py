"""make: a manual (a docs folder) to a built, evaluated, audited skill in one command; folder input for extract."""
import json
from pathlib import Path

from click.testing import CliRunner

from book2skill import build as build_mod
from book2skill import extract as extract_mod
from book2skill.cli import main

QA = (
    '{"q": "how do I chain commands in Windows PowerShell 5.1?", "must": ["semicolon"]}\n'
    '{"q": "which operator exists only in PowerShell 7?", "must": ["operator"]}\n'
    '{"q": "what does a pipeline pass between commands?", "must": ["objects"]}\n'
)


def _manual(root: Path) -> Path:
    docs = root / "manual"
    (docs / "sub").mkdir(parents=True)
    (docs / ".git").mkdir()
    (docs / "node_modules" / "pkg").mkdir(parents=True)
    (docs / "export" / "claude").mkdir(parents=True)
    (docs / "chain.md").write_text(
        "---\ntitle: Chaining\nms.date: 2026-01-01\n---\n# Chaining\n\nUse a semicolon to chain commands in Windows PowerShell 5.1. "
        "The && operator exists only in PowerShell 7.\n", encoding="utf-8")
    (docs / "sub" / "pipe.mdx").write_text("A pipeline passes objects, not text.\n", encoding="utf-8")
    (docs / "notes.png").write_bytes(b"\x89PNG not a doc")
    (docs / ".git" / "hidden.md").write_text("hidden-secret-word\n", encoding="utf-8")
    (docs / "node_modules" / "pkg" / "readme.md").write_text("vendored-word\n", encoding="utf-8")
    (docs / "export" / "claude" / "old.md").write_text("stale-export-word\n", encoding="utf-8")
    return docs


def _run(*args: str):
    return CliRunner().invoke(main, list(args))


def test_extract_reads_a_docs_folder(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    work = tmp_path / "work"
    receipt = extract_mod.extract(str(docs), work)
    text = (work / "full_text.txt").read_text(encoding="utf-8")
    assert receipt["kind"] == "folder" and receipt["files"] == 2
    assert "# file: chain.md" in text and "# file: sub/pipe.mdx" in text
    assert "semicolon" in text and "passes objects" in text
    assert "ms.date" not in text and "title: Chaining" not in text  # front matter dropped
    for gone in ("hidden-secret-word", "vendored-word", "stale-export-word", "PNG"):
        assert gone not in text


def test_extract_folder_does_not_read_its_own_output(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    work = docs / "work-inside"
    first = extract_mod.extract(str(docs), work)
    (work / "chunks").mkdir(exist_ok=True)
    (work / "chunks" / "0000.txt").write_text("ownoutputword\n", encoding="utf-8")
    (work / "notes.md").write_text("ownoutputword\n", encoding="utf-8")
    second = extract_mod.extract(str(docs), work)
    assert second["chars"] == first["chars"]
    assert second["skipped_own_output"] == 1
    assert "ownoutputword" not in (work / "full_text.txt").read_text(encoding="utf-8")


def test_extract_folder_glob_and_empty(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    work = tmp_path / "work"
    receipt = extract_mod.extract(str(docs), work, include="pipe.*")
    assert receipt["files"] == 1
    assert "semicolon" not in (work / "full_text.txt").read_text(encoding="utf-8")
    result = _run("extract", "--in", str(docs), "--out", str(tmp_path / "w2"), "--glob", "nothing-*.md")
    assert result.exit_code == 2 and "no .md" in result.output  # a usage error, not a traceback
    assert "Traceback" not in result.output


def _make_args(tmp_path: Path, docs: Path, *extra: str) -> list[str]:
    qa = tmp_path / "qa.jsonl"
    qa.write_text(QA, encoding="utf-8")
    return ["make", "--in", str(docs), "--name", "pwsh-demo", "--description", "Use when chaining commands in PowerShell.",
            "--qa", str(qa), "--work", str(tmp_path / "work" / "pwsh-demo"), "--skill", str(tmp_path / "skills" / "pwsh-demo"), *extra]


def test_make_one_command_builds_evals_audits(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    result = _run(*_make_args(tmp_path, docs))
    assert result.exit_code == 0, result.output
    for stage in ("extract  folder", "split ", "index ", "build ", "eval     3/3 = 1.000", "audit ", "fill     SKILL.md, glossary.md, patterns.md, cheatsheet.md"):
        assert stage in result.output, result.output
    skill = tmp_path / "skills" / "pwsh-demo"
    assert (skill / "SKILL.md").is_file() and (skill / "references" / "sources.md").is_file()
    assert json.loads((skill / "eval_report.json").read_text(encoding="utf-8"))["rate"] == 1.0
    receipt = json.loads((tmp_path / "work" / "pwsh-demo" / "make.json").read_text(encoding="utf-8"))
    assert receipt["gate"] == "pass" and receipt["stages"]["extract"]["files"] == 2
    assert receipt["placeholders"] == ["SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md"]
    assert not (tmp_path / "dist").exists()  # no --target, no export


def test_make_export_is_held_until_an_author_wrote_the_placeholders(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    held = _run(*_make_args(tmp_path, docs, "--target", "claude", "--out", str(tmp_path / "dist")))
    assert held.exit_code != 0 and "export held" in held.output and "glossary.md" in held.output
    assert not (tmp_path / "dist").exists()
    skill = tmp_path / "skills" / "pwsh-demo"
    (skill / "SKILL.md").write_text(
        "---\nname: pwsh-demo\ndescription: Use when chaining commands in PowerShell.\n---\nChain with a semicolon in 5.1.\n", encoding="utf-8")
    for fname in ("glossary.md", "patterns.md", "cheatsheet.md"):
        (skill / fname).write_text(f"# {fname}\n\nwritten by hand\n", encoding="utf-8")
    again = _run(*_make_args(tmp_path, docs, "--target", "claude", "--target", "codex", "--out", str(tmp_path / "dist")))
    assert again.exit_code == 0, again.output
    assert "build    skipped" in again.output  # the author's SKILL.md was not overwritten
    assert "Chain with a semicolon in 5.1." in (skill / "SKILL.md").read_text(encoding="utf-8")
    for target in ("claude", "codex"):
        dest = tmp_path / "dist" / target / "pwsh-demo"
        assert (dest / "SKILL.md").is_file() and (dest / ".lock.json").is_file()
        assert not (dest / "export").exists()
    # --rebuild gives the scaffold back
    rebuilt = _run(*_make_args(tmp_path, docs, "--rebuild"))
    assert rebuilt.exit_code == 0 and build_mod.scaffold_leftovers(skill) == ["SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md"]


def test_make_gate_refuses_a_failing_skill(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    args = _make_args(tmp_path, docs, "--target", "claude", "--out", str(tmp_path / "dist"))
    Path(args[args.index("--qa") + 1]).write_text(
        '{"q": "what about zzzznothere?", "must": ["zzzznothere"]}\n{"q": "what about qqqqmissing?", "must": ["qqqqmissing"]}\n', encoding="utf-8")
    result = _run(*args)
    assert result.exit_code != 0 and "eval gate refused" in result.output and "fix the skill, not the test" in result.output
    assert not (tmp_path / "dist").exists()


def test_make_refuses_early(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    ok = _make_args(tmp_path, docs)
    # a name that breaks the rule or does not match the skill dir
    bad = list(ok)
    bad[bad.index("--name") + 1] = "Bad_Name"
    result = _run(*bad)
    assert result.exit_code == 2 and "a-z0-9-" in result.output
    # no QA file
    nope = list(ok)
    nope[nope.index("--qa") + 1] = str(tmp_path / "missing.jsonl")
    result = _run(*nope)
    assert result.exit_code == 2 and "--qa" in result.output and "not found" in result.output
    # work and skill inside each other
    nested = list(ok)
    nested[nested.index("--work") + 1] = str(tmp_path / "skills" / "pwsh-demo" / "work")
    result = _run(*nested)
    assert result.exit_code == 2 and "inside each other" in result.output
    # output inside the source folder: the next run would read it
    inside = list(ok)
    inside[inside.index("--work") + 1] = str(docs / "work")
    result = _run(*inside)
    assert result.exit_code == 2 and "inside the source folder" in result.output
    assert not (tmp_path / "skills" / "pwsh-demo").exists()  # nothing was built before a refusal


def test_make_refuses_wrong_shaped_qa(tmp_path: Path) -> None:
    docs = _manual(tmp_path)
    args = _make_args(tmp_path, docs)
    Path(args[args.index("--qa") + 1]).write_text(
        '{"question": "how do I chain commands?", "answer": "semicolon", "keywords": ["semicolon"]}\n', encoding="utf-8")
    result = _run(*args)
    assert result.exit_code == 2, result.output
    assert '--qa' in result.output and 'must be {"q", "must"}' in result.output
    assert "got keys: answer, keywords, question" in result.output
    assert "Traceback" not in result.output
    assert not (tmp_path / "skills" / "pwsh-demo").exists()  # refused before anything was built


def test_scaffold_leftovers_reads_the_real_scaffold(tmp_path: Path) -> None:
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("chapter about leases", encoding="utf-8")
    skill = tmp_path / "demo-skill"
    build_mod.build(work, skill, "demo-skill", "demo")
    assert build_mod.scaffold_leftovers(skill) == ["SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md"]
    (skill / "patterns.md").write_text("# Patterns\n\nreal pattern\n", encoding="utf-8")
    assert "patterns.md" not in build_mod.scaffold_leftovers(skill)
