"""Preview-then-install steal: full SKILL.md + source repo + install count."""
import ast
import json
from pathlib import Path

import mcp_server.preview_helper as ph

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
HELPER = ROOT / "mcp_server" / "preview_helper.py"


def _real_skill() -> str:
    if (SKILLS / "progit-branching" / "SKILL.md").is_file():
        return "progit-branching"
    for entry in sorted(SKILLS.iterdir()):
        if (entry / "SKILL.md").is_file():
            return entry.name
    raise AssertionError("no built skills to preview")


def test_full_skill_md_not_truncated() -> None:
    skill = _real_skill()
    expected = (SKILLS / skill / "SKILL.md").read_text(encoding="utf-8")
    preview = ph.build_preview(skill)
    assert preview["ok"] is True
    assert expected != ""
    assert preview["skill_md"] == expected
    assert preview["chars"] == len(expected)
    assert preview["file"] == "SKILL.md"


def test_source_repo_extraction_prefers_sources_file(tmp_path) -> None:
    demo = tmp_path / "demo"
    (demo / "references").mkdir(parents=True)
    (demo / "SKILL.md").write_text("# demo\n", encoding="utf-8")
    (demo / "references" / "sources.md").write_text(
        "Upstream https://github.com/BurntSushi/ripgrep plus docs.\n", encoding="utf-8"
    )
    assert ph.read_source_repo("demo", tmp_path) == "https://github.com/BurntSushi/ripgrep"
    preview = ph.build_preview("demo", tmp_path)
    assert preview["ok"] is True
    assert preview["source_repo"] == "https://github.com/BurntSushi/ripgrep"


def test_source_repo_falls_back_to_skill_body(tmp_path) -> None:
    demo = tmp_path / "demo"
    demo.mkdir(parents=True)
    (demo / "SKILL.md").write_text(
        "See https://github.com/skillsgate/skillsgate for the donor.\n", encoding="utf-8"
    )
    assert ph.read_source_repo("demo", tmp_path) == "https://github.com/skillsgate/skillsgate"


def test_install_count_and_downloads_are_honest() -> None:
    skill = _real_skill()
    preview = ph.build_preview(skill)
    assert preview["install_count"] == 1
    assert preview["installs"] == 1
    assert isinstance(preview["downloads"], int) and preview["downloads"] >= 0
    assert ph.read_install_count("no-such-skill-xyz") == 0
    assert ph.read_downloads("no-such-skill-xyz") == 0


def test_block_carries_all_three_fields() -> None:
    skill = _real_skill()
    preview = ph.build_preview(skill)
    block = preview["block"]
    assert preview["informed"] is True
    assert "source repo:" in block.lower()
    assert "install count:" in block.lower()
    assert preview["skill_md"] in block
    json.dumps(preview)


def test_unknown_and_traversal_refuse() -> None:
    bad = ph.build_preview("no-such-skill-xyz")
    assert bad["ok"] is False and bad["skill"] == "no-such-skill-xyz"
    for name in ("../other", "a/b", "padded "):
        refused = ph.build_preview(name)
        assert refused["ok"] is False, name
        assert ph.read_skill_md(name) == ""
        assert ph.read_source_repo(name) == ""
        assert ph.read_install_count(name) == 0
    assert ph.build_preview("")["ok"] is False


def test_stdlib_only_no_network() -> None:
    tree = ast.parse(HELPER.read_text(encoding="utf-8"))
    allowed = {"__future__", "json", "re", "pathlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in allowed, alias.name
        elif isinstance(node, ast.ImportFrom):
            assert (node.module or "").split(".")[0] in allowed, node.module
    src = HELPER.read_text(encoding="utf-8")
    for token in ("urlopen", "requests", "httpx", "http.client", "socket", "urllib"):
        assert token not in src, token


def test_attribution_present() -> None:
    text = HELPER.read_text(encoding="utf-8")
    assert "skillsgate/skillsgate" in text
    assert "7acf56e" in text
    assert "MIT" in text
    assert "https://github.com/skillsgate/skillsgate" in text
    assert "_index.tsx" in text
