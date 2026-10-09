"""Steal report human summary beside audit JSON."""
import json
import sys
from pathlib import Path

from book2skill import audit as audit_mod


def _skill(tmp_path, name="demo-skill", body_chars=12000):
    skill = tmp_path / name
    (skill / "references").mkdir(parents=True)
    body = "x " * (body_chars // 2)
    description = "Use when testing the steal report summary with enough characters here."
    head = chr(10).join(["---", "name: " + name, "description: " + description, "---"])
    text = head + chr(10) + body + chr(10)
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    sources = "# Sources" + chr(10) + chr(10) + "- 0000.txt" + chr(10)
    (skill / "references" / "sources.md").write_text(sources, encoding="utf-8")
    return skill


def test_summary_names_over_budget_number(tmp_path, capsys):
    skill = _skill(tmp_path)
    report = audit_mod.audit(skill)
    out = capsys.readouterr()
    text = audit_mod.human_summary(report)
    assert str(report["body_tokens"]) in text
    assert "over budget" in text
    assert str(report["body_tokens"]) in out.err
    assert "audit" in out.err
    assert "#" in out.err
    assert "body" in out.err


def test_no_color_strips_codes(monkeypatch):
    esc = chr(27) + "["
    report = {"skill": "skills/demo-skill", "body_tokens": 3123, "body_budget": 2000, "total_tokens": 3500, "over_budget": True, "flags": ["body over budget (3123 > 2000 tokens)"]}
    monkeypatch.setattr(sys.stderr, "isatty", lambda: True)
    monkeypatch.delenv("NO_COLOR", raising=False)
    colored = audit_mod.human_summary(report)
    assert esc in colored
    monkeypatch.setenv("NO_COLOR", "1")
    plain = audit_mod.human_summary(report)
    assert esc not in plain
    assert "3123" in plain


def test_json_record_unchanged(tmp_path, capsys):
    skill = _skill(tmp_path, name="tiny-skill", body_chars=200)
    report = audit_mod.audit(skill)
    out = capsys.readouterr()
    expected = {"skill", "total_tokens", "sections", "always_loaded_tokens", "body_tokens", "references_tokens", "body_budget", "over_budget", "description", "name_check", "broken_links", "flags"}
    assert set(report.keys()) == expected
    parsed = json.loads(out.out)
    assert parsed["body_tokens"] == report["body_tokens"]
    assert parsed["total_tokens"] == report["total_tokens"]
    assert "audit" in out.err
