"""behavetree-how: every claim of SKILL.md run against the real script.

The script is started as a real subprocess with stdin closed (headless: no prompts). The three stock tests (--help runs,
SKILL.md documents what the script prints, an installed copy runs through pwsh) are written once in tests/skill_stock.py;
this file calls them and holds the tests of the skill's own work.
"""
from pathlib import Path

import pytest

import skill_stock as stock
from skill_stock import live

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "behavetree-how"
SCRIPT = SKILL / "scripts" / "behavetree_how.py"
pytestmark = pytest.mark.skipif(not SCRIPT.is_file(), reason="skill not built yet")

# Lines SKILL.md must carry exactly as the script prints them. The success line is the OK line below.
NEEDLES = ("OK", "ERROR", "exit 2")

GOOD_XML = """<root BTCPP_format="4">
  <BehaviorTree ID="MainTree">
    <Sequence name="root">
      <CheckBattery name="battery_ok"/>
      <SaySomething message="hi"/>
    </Sequence>
  </BehaviorTree>
</root>
"""


def run_tool(*args: str):
    """The script as a subprocess, stdin closed. Use it in the tests of the real work below."""
    return stock.run_script(SCRIPT, *args)


def write_xml(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_help_runs_without_a_prompt() -> None:
    stock.help_runs(SCRIPT, "--input", "--out")


def test_skill_md_documents_what_the_script_prints() -> None:
    stock.skill_md_documents(SKILL, NEEDLES)


@live
def test_an_installed_copy_runs_from_another_folder_through_pwsh(tmp_path: Path) -> None:
    """Install the skill like another repo does, then run it from pwsh from another folder."""
    copy = stock.installed_copy(tmp_path, "behavetree-how", "scripts/behavetree_how.py", skills=SKILL.parent)
    code, said = copy.run("--help")
    assert code == 0 and "--input" in said
    copy.assert_nothing_written_elsewhere()


def test_good_tree_passes_and_writes_summary(tmp_path: Path) -> None:
    """A tree with root BTCPP_format 4 and one MainTree prints OK and writes the summary."""
    src = write_xml(tmp_path, "good.xml", GOOD_XML)
    out = tmp_path / "good.txt"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 0, r.stdout + r.stderr
    assert r.stdout.split()[0] == "OK" and "MainTree" in r.stdout
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "trees: MainTree" and lines[1] == "nodes: 4"


def test_missing_format_is_refused_without_output(tmp_path: Path) -> None:
    """A root tag without BTCPP_format 4 is refused with ERROR and exit 2, writing nothing."""
    src = write_xml(tmp_path, "bad.xml", GOOD_XML.replace(' BTCPP_format="4"', ""))
    out = tmp_path / "bad.txt"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and r.stdout.split()[0] == "ERROR"
    assert not out.exists(), "a refused run must write nothing"


def test_decorator_with_two_children_is_refused(tmp_path: Path) -> None:
    """A decorator owns exactly one child: an Inverter with two children is refused."""
    body = GOOD_XML.replace("<CheckBattery name=\"battery_ok\"/>",
                            "<Inverter><CheckBattery name=\"a\"/><CheckBattery name=\"b\"/></Inverter>")
    src = write_xml(tmp_path, "dec.xml", body)
    out = tmp_path / "dec.txt"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and "exactly one child" in r.stdout
    assert not out.exists(), "a refused run must write nothing"


def test_subtree_with_unknown_id_is_refused(tmp_path: Path) -> None:
    """A SubTree ID must name a BehaviorTree block in the same file."""
    body = GOOD_XML.replace("<SaySomething message=\"hi\"/>", "<SubTree ID=\"NoSuchTree\"/>")
    src = write_xml(tmp_path, "sub.xml", body)
    out = tmp_path / "sub.txt"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and "NoSuchTree" in r.stdout
    assert not out.exists(), "a refused run must write nothing"


def test_leaf_with_children_is_refused(tmp_path: Path) -> None:
    """A leaf tag must not have element children."""
    body = GOOD_XML.replace("<CheckBattery name=\"battery_ok\"/>",
                            "<CheckBattery name=\"battery_ok\"><SaySomething message=\"hi\"/></CheckBattery>")
    src = write_xml(tmp_path, "leaf.xml", body)
    out = tmp_path / "leaf.txt"
    r = run_tool("--input", str(src), "--out", str(out))
    assert r.returncode == 2 and "must not have children" in r.stdout
    assert not out.exists(), "a refused run must write nothing"


def test_missing_input_file_is_refused(tmp_path: Path) -> None:
    """A missing --input file is refused with ERROR and exit 2, writing nothing."""
    out = tmp_path / "missing.txt"
    r = run_tool("--input", str(tmp_path / "nope.xml"), "--out", str(out))
    assert r.returncode == 2 and r.stdout.split()[0] == "ERROR"
    assert not out.exists(), "a refused run must write nothing"
