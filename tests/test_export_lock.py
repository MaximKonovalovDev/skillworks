"""K-16 [S01-C2]: export writes .lock.json {name, version, eval-rate, target, date} per target."""
import json
from pathlib import Path

from book2skill import export as export_mod


def test_export_writes_lock_per_target(tmp_path: Path) -> None:
    skill = tmp_path / "progit-branching"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: progit-branching\ndescription: demo\nversion: 0.1.0\nauthor: skillworks\ntags: []\n---\n",
        encoding="utf-8",
    )
    out = tmp_path / "dist"
    report = {"rate": 1.0, "total": 1, "passed": 1}
    for target in ("claude", "codex"):
        export_mod.export(skill, target, out, eval_report=report)
    for target in ("claude", "codex"):
        lock = json.loads((out / target / skill.name / ".lock.json").read_text(encoding="utf-8"))
        assert set(lock) == {"name", "version", "eval-rate", "target", "date"}
        assert lock["name"] == "progit-branching"
        assert lock["version"] == "0.1.0"
        assert lock["eval-rate"] == 1.0
        assert lock["target"] == target
        assert len(lock["date"]) == 10  # UTC YYYY-MM-DD
    # version defaults to 0.1.0 when SKILL.md frontmatter has none
    bare = tmp_path / "bare-skill"
    bare.mkdir()
    (bare / "SKILL.md").write_text("---\nname: bare-skill\ndescription: demo\n---\n", encoding="utf-8")
    export_mod.export(bare, "claude", out, eval_report=report)
    bare_lock = json.loads((out / "claude" / bare.name / ".lock.json").read_text(encoding="utf-8"))
    assert bare_lock["version"] == "0.1.0"
