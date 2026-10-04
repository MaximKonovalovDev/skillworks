"""pipe-run: every claim of SKILL.md and references/cost-model.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). Fast tests run always; the `live`
one installs a copy the way another repo would and drives it through pwsh.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

ROOT = g.ROOT
SKILL = g.SKILLS / "pipe-run"
SCRIPT = SKILL / "scripts" / "pipe_run.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")


LEGACY = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")  # a pipe set to a Western code page, as on a stock Windows PC


def run_pipe(*args: str, script: Path = SCRIPT, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL, timeout=60, cwd=cwd, env=env)


def items(tmp_path: Path, files: dict[str, bytes]) -> Path:
    src = tmp_path / "items"
    src.mkdir()
    for name, data in files.items():
        (src / name).write_bytes(data)
    return src


def test_pipe_run_cap_dry_run_and_run(tmp_path: Path) -> None:
    src = tmp_path / "items"
    src.mkdir()
    (src / "a.txt").write_text("x" * 400, encoding="utf-8")  # 100 tokens
    (src / "b.txt").write_text("y" * 200, encoding="utf-8")  # 50 tokens
    spend = 150
    out = tmp_path / "out"

    refused = run_pipe("--input", str(src), "--out", str(out), "--cap", "100")
    assert refused.returncode == 2
    assert refused.stdout.strip() == "ERROR over cap: spend 150 tokens > cap 100 tokens, refused; nothing written"
    assert not out.exists()  # refused run writes nothing

    dry = run_pipe("--input", str(src), "--out", str(out), "--cap", "1000", "--dry-run")
    assert dry.returncode == 0
    assert dry.stdout.strip() == f"DRY-RUN 2 items spend {spend} tokens (cap 1000)"
    assert not out.exists()  # dry-run changes nothing

    run = run_pipe("--input", str(src), "--out", str(out), "--cap", "1000")
    assert run.returncode == 0
    assert run.stdout.strip() == f"RUN 2 items spend {spend}/1000 tokens"
    assert (out / "a.txt").read_text(encoding="utf-8") == "x" * 400
    assert (out / "b.txt").read_text(encoding="utf-8") == "y" * 200
    receipt = json.loads((out / "receipt.json").read_text(encoding="utf-8"))
    assert receipt == {"tool": "pipe-run", "items": 2, "spend": spend, "cap": 1000}

    again = run_pipe("--input", str(src), "--out", str(tmp_path / "out2"), "--cap", "1000")
    assert again.returncode == 0
    assert again.stdout.strip() == run.stdout.strip()  # repeatable batch


@live
def test_the_cap_is_a_ceiling_spend_equal_to_it_runs(tmp_path: Path) -> None:
    src = items(tmp_path, {"a.txt": b"x" * 400})  # 100 tokens
    assert run_pipe("--input", str(src), "--out", str(tmp_path / "o1"), "--cap", "100").stdout.strip() == "RUN 1 items spend 100/100 tokens"
    r = run_pipe("--input", str(src), "--out", str(tmp_path / "o2"), "--cap", "99")
    assert r.returncode == 2 and "spend 100 tokens > cap 99 tokens" in r.stdout and not (tmp_path / "o2").exists()
    r = run_pipe("--input", str(src), "--out", str(tmp_path / "o3"), "--cap", "0")
    assert r.returncode == 2 and not (tmp_path / "o3").exists()


@live
def test_the_price_of_an_item_is_chars_over_four_with_a_minimum_of_one(tmp_path: Path) -> None:
    hebrew = ("א" * 8).encode("utf-8")  # 8 characters, 16 bytes: priced by characters
    src = items(tmp_path, {"empty.txt": b"", "three.txt": b"abc", "seven.txt": b"a" * 7, "eight.txt": b"a" * 8, "he.txt": hebrew})
    dry = run_pipe("--input", str(src), "--out", str(tmp_path / "o"), "--cap", "1000", "--dry-run").stdout.strip()
    assert dry == "DRY-RUN 5 items spend 7 tokens (cap 1000)", dry  # 1 (empty) + 1 (3 chars) + 1 (7) + 2 (8) + 2 (8 Hebrew letters)


@live
def test_a_line_break_costs_one_character_on_every_system(tmp_path: Path) -> None:
    (tmp_path / "w").mkdir()
    (tmp_path / "w" / "crlf.txt").write_bytes(b"ab\r\n" * 4)  # 16 bytes, 12 characters once a line break counts one
    (tmp_path / "w" / "lf.txt").write_bytes(b"ab\n" * 4)     # 12 bytes, 12 characters
    dry = run_pipe("--input", str(tmp_path / "w"), "--out", str(tmp_path / "o"), "--cap", "1000", "--dry-run").stdout.strip()
    assert dry == "DRY-RUN 2 items spend 6 tokens (cap 1000)", dry  # 3 + 3


@live
def test_only_top_level_txt_files_are_items_in_any_letter_case(tmp_path: Path) -> None:
    src = items(tmp_path, {"a.txt": b"x" * 40, "B.TXT": b"y" * 40, "c.md": b"z" * 400, "d.txt.bak": b"z" * 400, "noext": b"z" * 400})
    (src / "sub").mkdir()
    (src / "sub" / "deep.txt").write_bytes(b"z" * 400)
    (src / "folder.txt").mkdir()  # a folder named like an item is not an item
    out = tmp_path / "out"
    r = run_pipe("--input", str(src), "--out", str(out), "--cap", "1000")
    assert r.stdout.strip() == "RUN 2 items spend 20/1000 tokens", r.stdout + r.stderr
    assert sorted(p.name for p in out.iterdir()) == ["B.TXT", "a.txt", "receipt.json"]


@live
def test_items_are_copied_byte_for_byte(tmp_path: Path) -> None:
    data = {"lf.txt": b"one\ntwo\n", "crlf.txt": b"one\r\ntwo\r\n", "nonl.txt": b"no newline at the end", "bom.txt": b"\xef\xbb\xbfbom\n",
            "mixed.txt": b"a\r\nb\nc\rd", "he.txt": "שלום\n".encode("utf-8")}
    src = items(tmp_path, data)
    out = tmp_path / "out"
    r = run_pipe("--input", str(src), "--out", str(out), "--cap", "10000")
    assert r.returncode == 0, r.stdout + r.stderr
    for name, blob in data.items():
        assert (out / name).read_bytes() == blob, name


@live
def test_dry_run_over_the_cap_still_exits_zero_and_writes_nothing(tmp_path: Path) -> None:
    src = items(tmp_path, {"a.txt": b"x" * 4000})
    out = tmp_path / "out"
    r = run_pipe("--input", str(src), "--out", str(out), "--cap", "10", "--dry-run")
    assert r.returncode == 0 and r.stdout.strip() == "DRY-RUN 1 items spend 1000 tokens (cap 10)"
    assert not out.exists()


@live
def test_empty_input_runs_with_zero_items(tmp_path: Path) -> None:
    src = items(tmp_path, {})
    out = tmp_path / "out"
    r = run_pipe("--input", str(src), "--out", str(out), "--cap", "0")
    assert r.returncode == 0 and r.stdout.strip() == "RUN 0 items spend 0/0 tokens"
    assert json.loads((out / "receipt.json").read_text(encoding="utf-8")) == {"tool": "pipe-run", "items": 0, "spend": 0, "cap": 0}


@live
def test_an_item_that_is_not_utf8_text_is_refused_before_anything_is_written(tmp_path: Path) -> None:
    src = items(tmp_path, {"a.txt": b"fine", "z-binary.txt": b"\xff\xfe\x00 not text"})
    out = tmp_path / "out"
    for extra in ([], ["--dry-run"]):
        r = run_pipe("--input", str(src), "--out", str(out), "--cap", "1000", *extra)
        assert r.returncode == 2 and r.stdout.startswith("ERROR refused:") and "z-binary.txt" in r.stdout and "Traceback" not in r.stderr, r.stdout + r.stderr
        assert not out.exists()


@live
def test_a_hebrew_file_name_in_a_message_does_not_crash_a_legacy_code_page_pipe(tmp_path: Path) -> None:
    src = items(tmp_path, {"שלום.txt": b"\xff\xfe\x00 binary"})
    r = run_pipe("--input", str(src), "--out", str(tmp_path / "o"), "--cap", "10", env=LEGACY)
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused: שלום.txt is not UTF-8 text"), r.stdout + r.stderr
    assert "Traceback" not in r.stderr


@pytest.mark.parametrize("case,needle", [
    ("missing-input", "ERROR input dir missing:"),
    ("negative-cap", "ERROR cap must be >= 0, got -1"),
    ("out-is-input", "ERROR refused: --out is the input dir"),
    ("out-is-a-file", "ERROR refused: --out is a file"),
])
@live
def test_bad_input_is_an_error_with_exit_two(tmp_path: Path, case: str, needle: str) -> None:
    src = items(tmp_path, {"a.txt": b"abcd"})
    (tmp_path / "a_file").write_text("keep me", encoding="utf-8")
    out = tmp_path / "o"
    args = {
        "missing-input": ["--input", str(tmp_path / "missing"), "--out", str(out), "--cap", "5"],
        "negative-cap": ["--input", str(src), "--out", str(out), "--cap", "-1"],
        "out-is-input": ["--input", str(src), "--out", str(src), "--cap", "5"],
        "out-is-a-file": ["--input", str(src), "--out", str(tmp_path / "a_file"), "--cap", "5"],
    }[case]
    before = sorted((p.name, p.read_bytes()) for p in tmp_path.rglob("*") if p.is_file())
    r = run_pipe(*args)
    assert r.returncode == 2 and r.stdout.startswith(needle) and "Traceback" not in r.stderr, r.stdout + r.stderr
    assert not out.exists()
    assert before == sorted((p.name, p.read_bytes()) for p in tmp_path.rglob("*") if p.is_file())


@live
def test_a_cap_that_is_not_a_whole_number_is_a_usage_error(tmp_path: Path) -> None:
    src = items(tmp_path, {"a.txt": b"abcd"})
    r = run_pipe("--input", str(src), "--out", str(tmp_path / "o"), "--cap", "ten")
    assert r.returncode == 2 and "invalid int value" in r.stderr and not (tmp_path / "o").exists()


@live
def test_a_second_run_into_the_same_out_overwrites_the_items_and_the_receipt(tmp_path: Path) -> None:
    src = items(tmp_path, {"a.txt": b"x" * 40})
    out = tmp_path / "out"
    run_pipe("--input", str(src), "--out", str(out), "--cap", "100")
    (src / "a.txt").write_bytes(b"y" * 80)
    assert run_pipe("--input", str(src), "--out", str(out), "--cap", "100").stdout.strip() == "RUN 1 items spend 20/100 tokens"
    assert (out / "a.txt").read_bytes() == b"y" * 80
    assert json.loads((out / "receipt.json").read_text(encoding="utf-8"))["spend"] == 20


def test_help_runs_without_a_prompt() -> None:
    r = run_pipe("--help")
    assert r.returncode == 0 and all(flag in r.stdout for flag in ("--input", "--out", "--cap", "--dry-run"))


def test_skill_md_documents_what_the_script_prints() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8") + (SKILL / "references" / "cost-model.md").read_text(encoding="utf-8")
    for needle in ("RUN <n> items spend <S>/<C> tokens", "DRY-RUN <n> items spend <S> tokens (cap <C>)",
                   "ERROR over cap: spend <S> tokens > cap <C> tokens, refused; nothing written", "exit 2", "UTF-8", "top level"):
        assert needle in text, needle


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh with paths that hold spaces."""
    sys.path.insert(0, str(ROOT / "tools"))
    import install_fleet_skills as inst
    skills = tmp_path / "other repo" / "skills"
    inst.install("pipe-run", skills)
    assert inst.stale("pipe-run", skills) == []
    script = skills / "pipe-run" / "scripts" / "pipe_run.py"
    src = tmp_path / "my items"
    src.mkdir()
    (src / "a.txt").write_text("x" * 400, encoding="utf-8")
    out = tmp_path / "my out"
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh 7 is not installed")

    def ps(cap: int, *flags: str) -> tuple[int, str]:
        cmd = f"& '{sys.executable}' '{script}' --input '{src}' --out '{out}' --cap {cap} {' '.join(flags)}; exit $LASTEXITCODE"
        r = subprocess.run([pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", cmd], cwd=elsewhere, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=120)
        return r.returncode, r.stdout.strip()

    assert ps(50) == (2, "ERROR over cap: spend 100 tokens > cap 50 tokens, refused; nothing written")
    assert not out.exists()
    assert ps(500, "--dry-run") == (0, "DRY-RUN 1 items spend 100 tokens (cap 500)") and not out.exists()
    assert ps(500) == (0, "RUN 1 items spend 100/500 tokens")
    assert (out / "a.txt").read_bytes() == b"x" * 400
    assert not list(elsewhere.iterdir())
