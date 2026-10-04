"""tools/arsenal_selftest.py: the arsenal tests of book2skill, cron_skip_clean, pipe_dry_run and edit_guard are real runs on
fixtures, and each fails when its tool is wrong (a selftest that cannot fail proves nothing)."""
import json
import sys
from pathlib import Path

import pytest

import skill_gates as g

sys.path.insert(0, str(g.ROOT / "tools"))
import arsenal_selftest as st  # noqa: E402

TOOLS = ["book2skill", "cron_skip_clean", "pipe_dry_run", "edit_guard"]


@pytest.mark.parametrize("tool", TOOLS)
def test_selftest_passes_on_the_real_tool(tool: str) -> None:
    result = st.TESTS[tool](st.declared(tool))
    assert result.failed == 0, "\n".join(result.lines)
    assert len(result.lines) >= 9, "a selftest checks more than that the script starts"


@pytest.mark.parametrize("stub_text", [
    "import sys; sys.exit(0)",                   # a tool that prints nothing and always succeeds
    "print('SKIP clean 0000000000000000 / RUN 1 items spend 1/1 tokens / EDIT GUARD PASS')",  # one that always claims success
])
@pytest.mark.parametrize("tool", TOOLS)
def test_selftest_fails_on_a_wrong_tool(tool: str, stub_text: str, tmp_path: Path) -> None:
    stub = tmp_path / "stub.py"
    stub.write_text(stub_text + "\n", encoding="utf-8")
    result = st.TESTS[tool]([sys.executable, str(stub)])
    assert result.failed >= 1, "\n".join(result.lines)


def test_arsenal_json_runs_these_four_tools_through_the_selftest_not_help() -> None:
    entries = {e["name"]: e for e in json.loads((g.ROOT / "arsenal.json").read_text(encoding="utf-8"))["tools"]}
    for tool in TOOLS:
        assert entries[tool]["test"] == ["python", "tools/arsenal_selftest.py", tool], tool
    helpers = [name for name, e in entries.items() if e["test"][-1] == "--help"]
    assert not set(TOOLS) & set(helpers)


def test_a_bad_name_is_refused() -> None:
    assert st.main(["nope"]) == 2 and st.main([]) == 2
