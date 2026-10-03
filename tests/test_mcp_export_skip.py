"""skill_search answers from a skill's canonical files, never from its export/ copies (same bug class as K-07)."""
from pathlib import Path

from test_mcp_skills_dir import _search_call, _stdio_session


def test_search_skips_export_folder_and_still_finds_real_files(tmp_path: Path) -> None:
    base = tmp_path / "skills"
    skill = base / "export-skip-demo"
    (skill / "references").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: export-skip-demo\ndescription: demo\n---\nzorblax lives in the real file\n", encoding="utf-8")
    (skill / "references" / "a.md").write_text("zorblax again in references\n", encoding="utf-8")
    stale = skill / "export" / "claude" / "export-skip-demo"
    stale.mkdir(parents=True)
    (stale / "SKILL.md").write_text("zorblax in a stale export copy\n", encoding="utf-8")
    (skill / "export" / "only-here.md").write_text("flumpwick only in the export folder\n", encoding="utf-8")

    found = _stdio_session([_search_call("export-skip-demo", "zorblax")], env_dir=str(base))
    text = found[0]["result"]["content"][0]["text"]
    assert "SKILL.md" in text and "references" in text
    assert "export" not in text.replace("export-skip-demo", "")

    gone = _stdio_session([_search_call("export-skip-demo", "flumpwick")], env_dir=str(base))
    assert "only-here.md" not in gone[0]["result"]["content"][0]["text"]
