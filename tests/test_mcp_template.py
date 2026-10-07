"""PIPE-1006-1: mcp-template pack stays green.

The pack is an original dependency-free rewrite (ToolBinding shape plus a
duplicate guard); no donor code is copied. This test proves the verbs, the
guard, both selftest entry points, and the packs catalog listing.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

PACK = Path(__file__).resolve().parent.parent / "packs" / "mcp-template"
CATALOG = Path(__file__).resolve().parent.parent / "packs" / "catalog.md"


def _load_server():
    spec = importlib.util.spec_from_file_location("mcp_template_server", PACK / "server.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_tools_ping_add_echo() -> None:
    server = _load_server()
    assert [t.name for t in server.list_tools()] == ["ping", "add", "echo"]
    assert server._TOOLS["ping"].fn() == "pong"
    assert server._TOOLS["add"].fn(2, 3) == 5
    assert server._TOOLS["echo"].fn("hi") == "hi"


def test_duplicate_guard_keeps_original(capsys) -> None:
    server = _load_server()

    @server.tool("ping", "dup attempt")
    def ping_dup():
        return "evil"

    assert server._TOOLS["ping"].fn() == "pong", "duplicate overwrote original"
    assert "duplicate tool 'ping'" in capsys.readouterr().err


def test_selftest_script_ends_pass() -> None:
    proc = subprocess.run(
        [sys.executable, "selftest.py"],
        cwd=PACK,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "SELFTEST PASS" in proc.stdout


def test_server_selftest_flag_ends_pass() -> None:
    proc = subprocess.run(
        [sys.executable, "server.py", "--selftest"],
        cwd=PACK,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stderr
    assert "SELFTEST PASS" in proc.stdout


def test_pack_listed_in_catalog() -> None:
    text = CATALOG.read_text(encoding="utf-8")
    assert "packs/mcp-template" in text, "mcp-template pack missing from catalog"
