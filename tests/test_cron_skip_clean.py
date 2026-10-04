"""cron-skip-clean: every claim of SKILL.md and references/state-format.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts) from a folder that is not the
repo. Fast tests run always; the `live` ones install a copy the way another repo would and drive it through pwsh.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g
import skill_stock as stock
from skill_gates import live

ROOT = g.ROOT
SKILL = g.SKILLS / "cron-skip-clean"
SCRIPT = SKILL / "scripts" / "cron_skip_clean.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")


LEGACY = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")  # a pipe set to a Western code page, as on a stock Windows PC


def tick(watch: Path, state: Path, script: Path = SCRIPT, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(script), "--watch", str(watch), "--state", str(state)],
                          capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=60, cwd=cwd, env=env)


def word(proc: subprocess.CompletedProcess) -> str:
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout.strip()


def make_watch(tmp_path: Path) -> tuple[Path, Path]:
    watch = tmp_path / "watched"
    watch.mkdir()
    (watch / "a.txt").write_text("alpha", encoding="utf-8")
    return watch, tmp_path / "state" / "cron.json"  # the state file lives outside the watch dir


def test_skip_on_clean_proven(tmp_path: Path) -> None:
    watch, state = make_watch(tmp_path)

    first = word(tick(watch, state))
    assert first.startswith("RUN ")
    assert state.is_file()

    second = word(tick(watch, state))
    assert second.startswith("SKIP clean ")
    assert second.split()[-1] == first.split()[-1]  # same fingerprint, no work

    (watch / "b.txt").write_text("beta", encoding="utf-8")
    third = word(tick(watch, state))
    assert third.startswith("RUN ")
    assert third.split()[-1] != second.split()[-1]  # change detected

    assert word(tick(watch, state)).startswith("SKIP clean ")  # clean again after refresh


@live
def test_a_skip_touches_nothing(tmp_path: Path) -> None:
    watch, state = make_watch(tmp_path)
    word(tick(watch, state))
    before, stamp = state.read_bytes(), state.stat().st_mtime_ns
    snapshot = sorted((p.relative_to(tmp_path).as_posix(), p.read_bytes()) for p in tmp_path.rglob("*") if p.is_file())
    assert word(tick(watch, state)).startswith("SKIP")
    assert state.read_bytes() == before and state.stat().st_mtime_ns == stamp
    assert snapshot == sorted((p.relative_to(tmp_path).as_posix(), p.read_bytes()) for p in tmp_path.rglob("*") if p.is_file())


@pytest.mark.parametrize("junk", [
    b"not json {", b"\xff\xfe\x00\x01", b"", b"[]", b"null", b'"text"', b"123", b"{}", b'{"fingerprint": 5}', b'{"fingerprint": null}',
])
@live
def test_a_missing_or_unusable_state_is_one_run_then_clean(tmp_path: Path, junk: bytes) -> None:
    watch, state = make_watch(tmp_path)
    state.parent.mkdir()
    state.write_bytes(junk)
    assert word(tick(watch, state)).startswith("RUN ")
    assert json.loads(state.read_text(encoding="utf-8"))["tool"] == "cron-skip-clean"
    assert word(tick(watch, state)).startswith("SKIP clean ")


@live
def test_the_content_decides_not_the_clock(tmp_path: Path) -> None:
    watch, state = make_watch(tmp_path)
    word(tick(watch, state))
    os.utime(watch / "a.txt", (1_000_000_000, 1_000_000_000))
    assert word(tick(watch, state)).startswith("SKIP"), "a new modified time with the same bytes is clean"
    (watch / "empty-folder").mkdir()
    assert word(tick(watch, state)).startswith("SKIP"), "a folder with no file in it is clean"
    (watch / "a.txt").write_text("alpHa", encoding="utf-8")
    assert word(tick(watch, state)).startswith("RUN"), "same size, one letter different"
    assert word(tick(watch, state)).startswith("SKIP")
    (watch / "a.txt").rename(watch / "z.txt")
    assert word(tick(watch, state)).startswith("RUN"), "a rename is a change"
    assert word(tick(watch, state)).startswith("SKIP")
    (watch / "sub").mkdir()
    (watch / "sub" / "deep.txt").write_text("x", encoding="utf-8")
    assert word(tick(watch, state)).startswith("RUN"), "files in subfolders count"
    assert word(tick(watch, state)).startswith("SKIP")
    (watch / "sub" / "deep.txt").unlink()
    assert word(tick(watch, state)).startswith("RUN"), "a deleted file is a change"


@live
def test_the_fingerprint_is_the_documented_one(tmp_path: Path) -> None:
    """state-format.md: sha256 over the files sorted by relative path, each as path, NUL, bytes, NUL, then count=N; 16 hex chars."""
    watch = tmp_path / "w"
    (watch / "sub").mkdir(parents=True)
    files = {"a.txt": b"alpha", "B.txt": b"beta\r\n", "sub/c.bin": bytes(range(256)), "שלום.txt": "ש".encode()}
    for rel, data in files.items():
        (watch / rel).write_bytes(data)
    digest = hashlib.sha256()
    for rel in sorted(files):
        digest.update(rel.encode("utf-8") + b"\0" + files[rel] + b"\0")
    digest.update(b"count=4")
    state = tmp_path / "s.json"
    out = word(tick(watch, state))
    assert out == "RUN " + digest.hexdigest()[:16]
    assert json.loads(state.read_text(encoding="utf-8")) == {"fingerprint": digest.hexdigest()[:16], "tool": "cron-skip-clean", "version": 1}


@live
def test_a_state_file_inside_the_watch_dir_is_refused(tmp_path: Path) -> None:
    watch, _ = make_watch(tmp_path)
    for inside in (watch / "state.json", watch / "deeper" / "state.json"):
        r = tick(watch, inside)
        assert r.returncode == 2 and r.stdout.startswith("ERROR refused:") and "inside the watch dir" in r.stdout, r.stdout + r.stderr
        assert not inside.exists()


@live
def test_a_missing_watch_dir_is_an_error_and_writes_no_state(tmp_path: Path) -> None:
    state = tmp_path / "state" / "cron.json"
    r = tick(tmp_path / "nope", state)
    assert r.returncode == 2 and r.stdout.startswith("ERROR watch dir missing:") and "Traceback" not in r.stderr
    assert not state.parent.exists()


@live
def test_a_hebrew_folder_name_in_a_message_does_not_crash_a_legacy_code_page_pipe(tmp_path: Path) -> None:
    gone = tmp_path / "שלום"
    r = tick(gone, tmp_path / "s.json", env=LEGACY)
    assert r.returncode == 2 and r.stdout.startswith("ERROR watch dir missing: ") and "שלום" in r.stdout, r.stdout + r.stderr
    assert "Traceback" not in r.stderr


def test_an_unreadable_file_is_an_error_not_a_traceback(tmp_path: Path, monkeypatch, capsys) -> None:
    spec = importlib.util.spec_from_file_location("cron_skip_clean_under_test", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    watch, state = make_watch(tmp_path)

    def locked(self):
        raise PermissionError(13, "Permission denied", str(self))

    monkeypatch.setattr(Path, "read_bytes", locked)
    monkeypatch.setattr(sys, "argv", ["cron_skip_clean.py", "--watch", str(watch), "--state", str(state)])
    assert mod.main() == 2
    out = capsys.readouterr().out
    assert out.startswith("ERROR cannot read") and "state untouched" in out
    assert not state.exists()


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--watch", "--state")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, ("RUN <fp>", "SKIP clean <fp>", "ERROR", "exit 2", "inside the watch dir"), "references/state-format.md")


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh with paths that hold spaces and Hebrew letters."""
    box = stock.installed_copy(tmp_path, "cron-skip-clean", "scripts/cron_skip_clean.py")
    watch = tmp_path / "my watch שלום"
    watch.mkdir()
    (watch / "a.txt").write_text("alpha", encoding="utf-8")
    state = tmp_path / "my state" / "cron.json"

    def ps() -> str:
        code, said = box.run("--watch", str(watch), "--state", str(state))
        assert code == 0, said
        return said

    first, second = ps(), ps()
    assert first.startswith("RUN ") and second == "SKIP clean " + first.split()[-1]
    (watch / "b.txt").write_text("beta", encoding="utf-8")
    assert ps().startswith("RUN ")
    box.assert_nothing_written_elsewhere()
