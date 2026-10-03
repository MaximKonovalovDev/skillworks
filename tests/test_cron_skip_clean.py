"""K-23 cron-skip-clean: RUN when dirty, SKIP when clean, RUN again on change."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("skills/cron-skip-clean/scripts/cron_skip_clean.py")


def run_tick(watch: Path, state: Path) -> str:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--watch", str(watch), "--state", str(state)],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    return proc.stdout.strip()


def test_skip_on_clean_proven(tmp_path: Path) -> None:
    watch = tmp_path / "watched"
    watch.mkdir()
    (watch / "a.txt").write_text("alpha", encoding="utf-8")
    state = tmp_path / "state" / "cron.json"  # outside the watch dir

    first = run_tick(watch, state)
    assert first.startswith("RUN ")
    assert state.is_file()

    second = run_tick(watch, state)
    assert second.startswith("SKIP clean ")
    assert second.split()[-1] == first.split()[-1]  # same fingerprint, no work

    (watch / "b.txt").write_text("beta", encoding="utf-8")
    third = run_tick(watch, state)
    assert third.startswith("RUN ")
    assert third.split()[-1] != second.split()[-1]  # change detected

    fourth = run_tick(watch, state)
    assert fourth.startswith("SKIP clean ")  # clean again after refresh
