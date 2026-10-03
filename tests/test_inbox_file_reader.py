"""K-25 inbox-file-reader: one item filed to the board line, code untouched, outsiders refused."""
import subprocess
import sys
from pathlib import Path

SCRIPT = Path("skills/inbox-file-reader/scripts/file_one_item.py")


def run_reader(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_inbox_file_reader_files_one_item(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox.md"
    inbox.write_text("ASK-7 file me first\nASK-8 stays queued\n", encoding="utf-8")
    board = tmp_path / "empire-inbox.md"
    board.write_text("# empire inbox\n", encoding="utf-8")
    code = tmp_path / "untouchable.py"
    code.write_text("print('code')\n", encoding="utf-8")
    code_before = code.read_bytes()

    filed = run_reader("--inbox", str(inbox), "--board", str(board))
    assert filed.returncode == 0
    assert filed.stdout.strip() == f"FILED ASK-7 file me first -> {board}"

    board_lines = board.read_text(encoding="utf-8").splitlines()
    assert board_lines[-1] == "- [ ] ASK-7 file me first"  # correct board line
    assert "ASK-8 stays queued" in inbox.read_text(encoding="utf-8")
    assert "ASK-7 file me first" not in inbox.read_text(encoding="utf-8")
    assert code.read_bytes() == code_before  # code files untouched

    refused_py = run_reader("--inbox", str(code), "--board", str(board))
    assert refused_py.returncode == 2
    assert "ERROR refused:" in refused_py.stdout
    assert code.read_bytes() == code_before
    assert board.read_text(encoding="utf-8").splitlines()[-1] == "- [ ] ASK-7 file me first"

    refused_board = run_reader("--inbox", str(inbox), "--board", str(code))
    assert refused_board.returncode == 2
    assert "ERROR refused:" in refused_board.stdout
    assert code.read_bytes() == code_before  # refused board path writes nothing
