"""inbox-file-reader: every claim of SKILL.md and references/isolation.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). Fast tests run always; the `live`
one installs a copy the way another repo does and drives it through pwsh.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g
import skill_stock as stock
from skill_gates import live

ROOT = g.ROOT
SKILL = g.SKILLS / "inbox-file-reader"
SCRIPT = SKILL / "scripts" / "file_one_item.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")


LEGACY = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")  # a pipe set to a Western code page, as on a stock Windows PC


def run_reader(*args: str, script: Path = SCRIPT, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=60, cwd=cwd, env=env)


def tree(root: Path) -> dict[str, bytes]:
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(root.rglob("*")) if p.is_file()}


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


@live
def test_one_item_per_run_in_order_and_only_the_two_files_change(tmp_path: Path) -> None:
    (tmp_path / "other.py").write_text("print(1)\n", encoding="utf-8")
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "keep.md").write_text("keep\n", encoding="utf-8")
    inbox, board = tmp_path / "in.md", tmp_path / "board.md"
    inbox.write_bytes(b"\n   \n  first item  \n\nsecond item\nthird item\n")
    board.write_bytes(b"# board\n- [x] old\n")
    before = tree(tmp_path)

    r = run_reader("--inbox", str(inbox), "--board", str(board))
    assert r.stdout.strip() == f"FILED first item -> {board}"
    after = tree(tmp_path)
    assert {k for k in after if after[k] != before.get(k)} == {"in.md", "board.md"}
    assert board.read_bytes() == b"# board\n- [x] old\n- [ ] first item\n"
    assert inbox.read_bytes() == b"\n   \n\nsecond item\nthird item\n", "every other line stays as it was, byte for byte"

    assert run_reader("--inbox", str(inbox), "--board", str(board)).stdout.strip() == f"FILED second item -> {board}"
    assert run_reader("--inbox", str(inbox), "--board", str(board)).stdout.strip() == f"FILED third item -> {board}"
    r = run_reader("--inbox", str(inbox), "--board", str(board))
    assert r.returncode == 2 and r.stdout.strip() == f"ERROR inbox empty: {inbox}; board untouched"
    assert board.read_bytes() == b"# board\n- [x] old\n- [ ] first item\n- [ ] second item\n- [ ] third item\n"


@live
def test_line_endings_of_the_other_lines_are_kept(tmp_path: Path) -> None:
    inbox, board = tmp_path / "in.md", tmp_path / "board.md"
    inbox.write_bytes(b"one\r\ntwo\r\nthree\n")
    board.write_bytes(b"# board\r\n")
    run_reader("--inbox", str(inbox), "--board", str(board))
    assert inbox.read_bytes() == b"two\r\nthree\n"
    assert board.read_bytes() == b"# board\r\n- [ ] one\r\n", "a board that uses CRLF gets a CRLF line"
    run_reader("--inbox", str(inbox), "--board", str(board))
    assert inbox.read_bytes() == b"three\n"


@live
def test_a_board_without_a_final_line_break_does_not_swallow_the_item(tmp_path: Path) -> None:
    inbox, board = tmp_path / "in.md", tmp_path / "board.md"
    inbox.write_bytes(b"one\n")
    board.write_bytes(b"# board")
    run_reader("--inbox", str(inbox), "--board", str(board))
    assert board.read_bytes() == b"# board\n- [ ] one\n"


@live
def test_a_byte_order_mark_stays_at_the_start_of_the_inbox_and_out_of_the_board(tmp_path: Path) -> None:
    inbox, board = tmp_path / "in.md", tmp_path / "board.md"
    inbox.write_bytes(b"\xef\xbb\xbfone\ntwo\n")
    run_reader("--inbox", str(inbox), "--board", str(board))
    assert board.read_bytes() == b"- [ ] one\n"
    assert inbox.read_bytes() == b"\xef\xbb\xbftwo\n"


@live
def test_a_board_that_cannot_be_written_leaves_the_inbox_alone(tmp_path: Path) -> None:
    inbox = tmp_path / "in.md"
    inbox.write_bytes(b"one\n")
    (tmp_path / "board.md").mkdir()  # a folder where the board file should be
    r = run_reader("--inbox", str(inbox), "--board", str(tmp_path / "board.md"))
    assert r.returncode == 2 and r.stdout.startswith("ERROR cannot write board") and "Traceback" not in r.stderr, r.stdout + r.stderr
    assert inbox.read_bytes() == b"one\n"


@live
def test_a_hebrew_item_is_filed_and_echoed_even_on_a_legacy_code_page_pipe(tmp_path: Path) -> None:
    inbox, board = tmp_path / "in.md", tmp_path / "board.md"
    inbox.write_bytes("שלום ASK-3\nnext\n".encode("utf-8"))
    r = run_reader("--inbox", str(inbox), "--board", str(board), env=LEGACY)
    assert r.returncode == 0 and r.stdout.startswith("FILED שלום ASK-3 -> "), r.stdout + r.stderr
    assert "Traceback" not in r.stderr
    assert board.read_bytes() == "- [ ] שלום ASK-3\n".encode("utf-8") and inbox.read_bytes() == b"next\n"


@live
def test_a_new_board_is_created_with_its_folders(tmp_path: Path) -> None:
    inbox = tmp_path / "in.md"
    inbox.write_bytes("שלום ASK-9\n".encode("utf-8"))
    board = tmp_path / "a" / "b" / "board.md"
    r = run_reader("--inbox", str(inbox), "--board", str(board))
    assert r.returncode == 0
    assert board.read_bytes() == "- [ ] שלום ASK-9\n".encode("utf-8")
    assert inbox.read_bytes() == b""


@live
@pytest.mark.parametrize("name", ["inbox.md", "inbox.MD", "inbox.markdown", "inbox.txt", "inbox.TXT"])
def test_allowed_suffixes(tmp_path: Path, name: str) -> None:
    inbox, board = tmp_path / name, tmp_path / ("board" + Path(name).suffix)
    inbox.write_bytes(b"x\n")
    assert run_reader("--inbox", str(inbox), "--board", str(board)).returncode == 0


@live
@pytest.mark.parametrize("bad", ["code.py", "run.ps1", "Makefile", "data.json", "inbox.md.py", ".md", "script.mjs"])
def test_a_path_outside_the_allowlist_is_refused_on_either_side(tmp_path: Path, bad: str) -> None:
    good_in, good_board, other = tmp_path / "in.md", tmp_path / "board.md", tmp_path / bad
    good_in.write_bytes(b"item\n")
    other.write_bytes(b"keep me\n")
    before = tree(tmp_path)
    for args in (["--inbox", str(other), "--board", str(good_board)], ["--inbox", str(good_in), "--board", str(other)]):
        r = run_reader(*args)
        assert r.returncode == 2 and r.stdout.startswith("ERROR refused:") and "outside allowlist" in r.stdout, r.stdout + r.stderr
        assert tree(tmp_path) == before, "neither file is created, truncated or appended to"
        assert sorted(p.name for p in tmp_path.iterdir()) == sorted(before)


@live
def test_the_same_file_twice_is_refused_even_spelled_differently(tmp_path: Path) -> None:
    (tmp_path / "d").mkdir()
    inbox = tmp_path / "in.md"
    inbox.write_bytes(b"item\n")
    before = tree(tmp_path)
    for spelled in (str(inbox), str(tmp_path / "d" / ".." / "in.md"), str(inbox).upper() if sys.platform == "win32" else str(inbox)):
        r = run_reader("--inbox", str(inbox), "--board", spelled)
        assert r.returncode == 2 and r.stdout.startswith("ERROR refused:") and "same file" in r.stdout, r.stdout + r.stderr
        assert tree(tmp_path) == before


@live
def test_a_missing_inbox_is_an_error_and_creates_nothing(tmp_path: Path) -> None:
    board = tmp_path / "newdir" / "board.md"
    r = run_reader("--inbox", str(tmp_path / "gone.md"), "--board", str(board))
    assert r.returncode == 2 and r.stdout.strip() == f"ERROR inbox missing: {tmp_path / 'gone.md'}; board untouched"
    assert not board.parent.exists()


@live
def test_an_empty_or_blank_inbox_is_an_error_and_the_board_is_untouched(tmp_path: Path) -> None:
    board = tmp_path / "board.md"
    board.write_bytes(b"# board\n")
    for blank in (b"", b"\n\n  \n\t\n"):
        inbox = tmp_path / "in.md"
        inbox.write_bytes(blank)
        r = run_reader("--inbox", str(inbox), "--board", str(board))
        assert r.returncode == 2 and r.stdout.strip() == f"ERROR inbox empty: {inbox}; board untouched"
        assert board.read_bytes() == b"# board\n" and inbox.read_bytes() == blank


@live
def test_an_inbox_that_is_not_utf8_text_is_an_error_not_a_traceback(tmp_path: Path) -> None:
    inbox, board = tmp_path / "in.md", tmp_path / "board.md"
    inbox.write_bytes(b"\xff\xfe\x00 binary\n")
    r = run_reader("--inbox", str(inbox), "--board", str(board))
    assert r.returncode == 2 and r.stdout.startswith("ERROR") and "not UTF-8" in r.stdout and "Traceback" not in r.stderr, r.stdout + r.stderr
    assert not board.exists() and inbox.read_bytes() == b"\xff\xfe\x00 binary\n"


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--inbox", "--board")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, ("FILED <item> -> <board>", "ERROR refused:", "ERROR inbox missing", "ERROR inbox empty", "not UTF-8", "exit 2",
                                     "same file", "- [ ] <item>"), "references/isolation.md")


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh with paths that hold spaces."""
    copy = stock.installed_copy(tmp_path, "inbox-file-reader", "scripts/file_one_item.py")
    box = tmp_path / "my box"
    box.mkdir()
    inbox, board = box / "empire inbox.md", box / "my board.md"
    inbox.write_bytes("ASK-1 first\nASK-2 second\n".encode("utf-8"))
    board.write_bytes(b"# board\n")

    def ps() -> tuple[int, str]:
        return copy.run("--inbox", str(inbox), "--board", str(board))

    assert ps() == (0, f"FILED ASK-1 first -> {board}")
    assert ps() == (0, f"FILED ASK-2 second -> {board}")
    code, said = ps()
    assert code == 2 and said.startswith("ERROR inbox empty")
    assert board.read_bytes() == b"# board\n- [ ] ASK-1 first\n- [ ] ASK-2 second\n"
    copy.assert_nothing_written_elsewhere()
