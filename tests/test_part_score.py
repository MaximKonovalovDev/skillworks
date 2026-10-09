"""K-30 smoke: tools/part_score.py exits 0 with one line per part, real data only."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_part_score_smoke() -> None:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "part_score.py")],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    lines = [line for line in proc.stdout.splitlines() if line.strip()]
    assert len(lines) >= 6, proc.stdout
    blob = proc.stdout
    for marker in ("P1", "P2", "P3", "P4", "P5", "workspace"):
        assert marker in blob, proc.stdout

def test_workspace_git_failure_is_loud(monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("part_score_loud", str(ROOT / "tools" / "part_score.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    def _boom(*args, **kwargs):
        raise OSError("git-boom-123")
    monkeypatch.setattr(mod.subprocess, "run", _boom)
    line = mod._workspace()
    assert line.startswith("workspace:")
    assert "UNKNOWN" in line
    assert "git-boom-123" in line
    assert "UNKNOWN (git " in line
