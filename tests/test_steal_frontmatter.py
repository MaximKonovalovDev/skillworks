"""STEAL frontcheck: typed file:line frontmatter errors in gates (stdlib-only)."""
from pathlib import Path

import book2skill.gates as g


def _one(text, path="SKILL.md", **kw):
    issues = g.lint_frontmatter_text(text, path=path, **kw)
    assert len(issues) == 1, issues
    return issues[0]


def test_issue_types_are_seven():
    assert tuple(g.FRONTMATTER_ISSUE_TYPES) == ("missing", "empty", "yaml", "type", "required", "warning", "io")


def test_missing():
    issue = _one("no frontmatter here\nbody\n")
    assert issue["type"] == "missing"
    assert issue["file"] == "SKILL.md" and issue["line"] == 1
    assert f"{issue['file']}:{issue['line']}" == "SKILL.md:1"


def test_empty():
    issue = _one("---\n---\nbody\n")
    assert issue["type"] == "empty"
    assert issue["line"] == 1


def test_yaml_unclosed_reports_file_line():
    issue = _one("---\nname: demo\ndescription: [unclosed\n---\nbody\n")
    assert issue["type"] == "yaml"
    assert issue["line"] == 3
    assert f"{issue['file']}:{issue['line']}" == "SKILL.md:3"
    assert "SKILL.md:3" in issue["msg"]


def test_type_list():
    issue = _one("---\n- just\n- list\n---\nbody\n")
    assert issue["type"] == "type"
    assert issue["line"] == 2


def test_required():
    issue = _one("---\nname: demo\nlicense: MIT\n---\nbody\n")
    assert issue["type"] == "required"
    assert issue["line"] == 2
    assert "description" in issue["msg"]


def test_warning_null():
    issue = _one("---\nname: demo\ndescription:\n---\nbody\n")
    assert issue["type"] == "warning"
    assert issue["line"] == 3
    assert "description" in issue["msg"]


def test_io(tmp_path: Path):
    missing = tmp_path / "nope.md"
    issues = g.lint_frontmatter_file(str(missing))
    assert len(issues) == 1 and issues[0]["type"] == "io"
    assert issues[0]["line"] == 1


def test_all_seven_types_detected_where_old_returned_empty():
    assert g.frontmatter("no frontmatter here\nbody\n") == {}
    cases = [
        g.lint_frontmatter_text("no frontmatter\nbody\n"),
        g.lint_frontmatter_text("---\n---\nbody\n"),
        g.lint_frontmatter_text("---\nname: demo\ndescription: [unclosed\n---\nbody\n"),
        g.lint_frontmatter_text("---\n- a\n- b\n---\nbody\n"),
        g.lint_frontmatter_text("---\nname: demo\n---\nbody\n"),
        g.lint_frontmatter_text("---\nname: demo\ndescription:\n---\nbody\n"),
        g.lint_frontmatter_file("C:/nope-steal-frontmatter-12345.md"),
    ]
    got = sorted(i[0]["type"] for i in cases)
    assert got == ["empty", "io", "missing", "required", "type", "warning", "yaml"]
    for issues in cases:
        issue = issues[0]
        assert set(issue) >= {"file", "line", "type", "msg"}
        assert f"{issue['file']}:{issue['line']}" in issue["msg"] or ":" in f"{issue['file']}:{issue['line']}"


def test_valid_folded_stays_clean():
    text = ("---\nname: demo\nlicense: MIT\ndescription: >-\n"
            "  Use when testing folded gates with enough characters to clear the length gate here ok?\n---\nbody\n")
    assert g.lint_frontmatter_text(text) == []
    assert g.frontmatter(text)["description"].startswith("Use when")