"""Regression for ARSENAL-B2S-JSON: audit JSON plus human summary broke json.loads.

The old tools/arsenal_selftest.py run() returned stdout+stderr combined;
book2skill audit prints JSON (~52 lines) to stdout and human_summary
("audit <label> / body ...") to stderr, so json.loads(out[out.index("{"):])
raised Extra data line 53 column 1. The fix separates the streams (parse
stdout only) plus a parse_report guard (raw_decode) for combined text.
"""
import json
import sys
from pathlib import Path as _Path

# Bare `pytest <file>` does not put the repo root on sys.path (only
# `python -m pytest` and `pytest tests/` do via cwd/rootdir), so insert
# root and tests dir before importing skill_gates/book2skill.
sys.path.insert(0, str(_Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(_Path(__file__).resolve().parent))

import pytest

import skill_gates as g

sys.path.insert(0, str(g.ROOT / "tools"))
import arsenal_selftest as st  # noqa: E402

from book2skill import audit as audit_mod


def _skill(tmp_path, name="leaseguide"):
    skill = tmp_path / name
    (skill / "references").mkdir(parents=True)
    desc = "Use when a queue item is stuck: leases and requeue"
    head = "\n".join(["---", "name: " + name, "description: " + desc, "---"])
    body = "A lease guards a queue item. " * 40
    (skill / "SKILL.md").write_text(head + "\n" + body + "\n", encoding="utf-8")
    (skill / "references" / "sources.md").write_text("# Sources\n", encoding="utf-8")
    return skill


def test_combined_output_parses_via_guard():
    report = {"skill": "skills/leaseguide", "body_budget": 2000, "over_budget": False, "total_tokens": 120}
    stdout = json.dumps(report, indent=2)
    stderr = audit_mod.human_summary(report)
    both = st.combined(stdout, stderr)
    # The old naive parse fails on the trailing human block: the bug.
    with pytest.raises(json.JSONDecodeError):
        json.loads(both[both.index("{"):])
    # The guard parses the same combined text.
    assert st.parse_report(both) == report
    # And stdout alone parses with either method.
    assert st.parse_report(stdout) == report
    assert json.loads(stdout) == report


def test_audit_stdout_is_json_only_stderr_is_human(tmp_path, capsys):
    skill = _skill(tmp_path)
    report = audit_mod.audit(skill)
    out = capsys.readouterr()
    assert out.out.strip().startswith("{")
    assert "body   " not in out.out
    assert json.loads(out.out)["body_budget"] == 2000
    assert "audit" in out.err and "body" in out.err
    assert st.parse_report(st.combined(out.out, out.err)) == json.loads(out.out)
    assert report["over_budget"] is False


def test_audit_quiet_prints_nothing(tmp_path, capsys):
    skill = _skill(tmp_path)
    report = audit_mod.audit(skill, quiet=True)
    out = capsys.readouterr()
    assert out.out == "" and out.err == ""
    assert report["body_budget"] == 2000
