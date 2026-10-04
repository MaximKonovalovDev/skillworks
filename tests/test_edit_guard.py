"""DRY-EDIT: edit_guard refuses a stale oldString with the rule quoted."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import edit_guard as eg  # noqa: E402

RULE = "re-read the file before editing"


def _crlf_tab_file(path: Path) -> Path:
    # Real CRLF bytes with a tab indent, written as bytes so the endings survive.
    path.write_bytes(b"def hello():\r\n\treturn 42\r\n\r\nprint(hello())\r\n")
    return path


def test_absent_string_refused_with_rule_quoted(tmp_path: Path, capsys) -> None:
    target = tmp_path / "code.py"
    target.write_text("def hello():\n    return 42\n", encoding="utf-8")
    rc = eg.main(["--file", str(target), "--old-string", "def hello():\n\treturn 43\n"])
    out = capsys.readouterr().out
    assert rc == 1
    assert RULE in out
    assert "closest line" in out


def test_crlf_file_diagnosed(tmp_path: Path, capsys) -> None:
    target = _crlf_tab_file(tmp_path / "code.py")
    # Stale copy: LF endings and spaces instead of the real tab.
    rc = eg.main(["--file", str(target), "--old-string", "def hello():\n    return 42\n"])
    out = capsys.readouterr().out
    assert rc == 1
    assert RULE in out
    assert "CRLF" in out
    assert "\\t" in out  # the real tab line is shown with its exact whitespace
    assert "\\r" in out or "no \\r" in out


def test_exact_match_passes(tmp_path: Path, capsys) -> None:
    target = _crlf_tab_file(tmp_path / "code.py")
    exact = target.read_bytes().decode("utf-8")
    want = "\treturn 42\r\n"
    assert want in exact
    rc = eg.main(["--file", str(target), "--old-string", want])
    out = capsys.readouterr().out
    assert rc == 0
    assert "EDIT GUARD PASS" in out


def test_command_line_help_exits_zero() -> None:
    root = Path(__file__).resolve().parent.parent
    assert subprocess.run([sys.executable, str(root / "tools" / "edit_guard.py"), "--help"],
                          capture_output=True, text=True).returncode == 0
