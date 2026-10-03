"""K-24 pipe-run: over-cap refused with spend quoted, dry-run clean, under-cap runs."""
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("skills/pipe-run/scripts/pipe_run.py")


def run_pipe(*args: str) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )
    return proc


def test_pipe_run_cap_dry_run_and_run(tmp_path: Path) -> None:
    src = tmp_path / "items"
    src.mkdir()
    (src / "a.txt").write_text("x" * 400, encoding="utf-8")  # 100 tokens
    (src / "b.txt").write_text("y" * 200, encoding="utf-8")  # 50 tokens
    spend = 150
    out = tmp_path / "out"

    refused = run_pipe("--input", str(src), "--out", str(out), "--cap", "100")
    assert refused.returncode != 0
    assert f"spend {spend} tokens" in refused.stdout  # spend quoted
    assert "> cap 100 tokens" in refused.stdout
    assert not out.exists()  # refused run writes nothing

    dry = run_pipe("--input", str(src), "--out", str(out), "--cap", "1000", "--dry-run")
    assert dry.returncode == 0
    assert dry.stdout.strip().startswith("DRY-RUN ")
    assert f"spend {spend} tokens" in dry.stdout
    assert not out.exists()  # dry-run changes nothing

    run = run_pipe("--input", str(src), "--out", str(out), "--cap", "1000")
    assert run.returncode == 0
    assert run.stdout.strip().startswith("RUN ")
    assert f"spend {spend}/1000 tokens" in run.stdout
    assert (out / "a.txt").read_text(encoding="utf-8") == "x" * 400
    assert (out / "b.txt").read_text(encoding="utf-8") == "y" * 200
    receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
    assert receipt == {"tool": "pipe-run", "items": 2, "spend": spend, "cap": 1000}

    again = run_pipe("--input", str(src), "--out", str(tmp_path / "out2"),
                     "--cap", "1000")
    assert again.returncode == 0
    assert again.stdout.strip() == run.stdout.strip()  # repeatable batch
