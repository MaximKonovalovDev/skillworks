"""Steal cliux checks."""
import os
from pathlib import Path

from click.testing import CliRunner

from book2skill.cli import _Live
from book2skill.cli import _live_enabled
from book2skill.cli import main


QA = "{\"q\": \"a?\", \"must\": [\"b\"]}\n"

def _manual(root):
    docs = root / "manual"
    (docs / "sub").mkdir(parents=True)
    (docs / "chain.md").write_text("# Chaining\n\nUse a semicolon to chain commands in Windows PowerShell 5.1. The operator exists only in PowerShell 7.\n", encoding="utf-8")
    (docs / "sub" / "pipe.mdx").write_text("A pipeline passes objects.\n", encoding="utf-8")
    return docs

def test_misuse_shows_usage_and_hint(tmp_path):
    docs = _manual(tmp_path)
    qa = tmp_path / "qa.jsonl"
    qa.write_text(QA, encoding="utf-8")
    args = ["make", "--in", str(docs), "--name", "Bad_Name", "--description", "Use when testing misuse.", "--qa", str(qa)]
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 2
    assert "Usage:" in result.output
    assert "Try" in result.output
    assert "--help" in result.output
    assert "Traceback" not in result.output

def test_no_ctxless_raises():
    text = Path("book2skill/cli.py").read_text(encoding="utf-8")
    assert text.count("raise click.UsageError(str(exc))") == 0
    assert "_misuse" in text
    assert "_Live" in text

def test_live_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    assert _live_enabled() is False
    monkeypatch.delenv("NO_COLOR", raising=False)

def test_live_finish_is_table(capsys):
    live = _Live()
    live._live = False
    live.say("extract  folder, 10 chars")
    live.say("split    1 chunks")
    live.finish()
    out = capsys.readouterr().out
    assert "extract  folder" in out
    assert "split    1 chunks" in out
    assert len(out.splitlines()) == 2

def test_make_scroll_is_short(tmp_path):
    docs = _manual(tmp_path)
    qa = tmp_path / "qa.jsonl"
    qa.write_text("{\"q\": \"how do I chain commands in Windows?\", \"must\": [\"semicolon\"]}\n{\"q\": \"what does a pipeline pass between commands?\", \"must\": [\"objects\"]}\n", encoding="utf-8")
    work = tmp_path / "work" / "demo"
    skill = tmp_path / "skills" / "demo"
    args = ["make", "--in", str(docs), "--name", "demo", "--description", "Use when chaining.", "--qa", str(qa), "--work", str(work), "--skill", str(skill)]
    result = CliRunner().invoke(main, args)
    assert result.exit_code == 0, result.output
    assert "extract  folder" in result.output
    assert "eval" in result.output
    assert len(result.output.splitlines()) <= 10, result.output

def test_audit_scroll_is_short(tmp_path):
    skill = tmp_path / "s"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: s\ndescription: Use when testing audit scroll with enough words to pass checks here.\n---\nBody text here.\n", encoding="utf-8")
    (skill / "glossary.md").write_text("# Glossary\n\nwritten\n", encoding="utf-8")
    result = CliRunner().invoke(main, ["audit", "--skill", str(skill)])
    assert len(result.output.splitlines()) <= 10, result.output
