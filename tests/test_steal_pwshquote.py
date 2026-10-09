"""Steal pwsh quote traps: space-path plus quote-char pass through guard verbatim."""
import importlib.util
import shutil
import subprocess
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("steal_run_spawn", ROOT / "skills" / "bash-spawn-guard" / "scripts" / "run_spawn.py")
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

def test_quote_space_path_gets_outer_single_quotes():
    assert MOD.pwsh_quote_arg("C:\\a b\\c.txt") == "\x27C:\\a b\\c.txt\x27"

def test_quote_quote_char_doubles_to_two_singles():
    assert MOD.pwsh_quote_arg("a\x27b") == "\x27a\x27\x27b\x27"

def test_quote_empty_becomes_two_singles():
    assert MOD.pwsh_quote_arg("") == "\x27\x27"

def test_guard_keeps_space_path_verbatim():
    argv = MOD.guard_pwsh_argv(["pwsh", "-NoLogo", "C:\\a b\\c.txt"])
    assert argv == ["pwsh", "-NoLogo", "C:\\a b\\c.txt"]

def test_guard_refuses_nested_bash_hatch():
    with pytest.raises(ValueError):
        MOD.guard_pwsh_argv(["bash", "-c", "echo hi"])

def test_guard_refuses_nested_sh_hatch():
    with pytest.raises(ValueError):
        MOD.guard_pwsh_argv(["sh", "-c", "echo hi"])

def test_pwsh_roundtrip_space_and_quote_verbatim():
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh 7 is not installed")
    cases = ["hello world", "a\x27b", "a[b]c", "price $5"]
    for original in cases:
        quoted = MOD.pwsh_quote_arg(original)
        argv = MOD.guard_pwsh_argv([pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "Write-Output " + quoted])
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        assert proc.returncode == 0
        assert proc.stdout.strip() == original

def test_pwsh_literalpath_space_file_verbatim(tmp_path):
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh 7 is not installed")
    d = tmp_path / "dir with space"
    d.mkdir()
    f = d / "note [1].txt"
    f.write_text("literal ok", encoding="utf-8")
    quoted = MOD.pwsh_quote_arg(str(f))
    argv = MOD.guard_pwsh_argv([pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", "Get-Content -LiteralPath " + quoted + " -Raw"])
    proc = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0
    assert proc.stdout.strip() == "literal ok"
