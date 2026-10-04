"""The stock tests of a fleet skill, written once.

Every fleet skill repeated the same three tests: `--help` runs without a prompt, SKILL.md documents what the script
prints, and an installed copy runs from another folder through pwsh. They live here; each skill's test file calls them
and keeps only the tests of its own work. `python tools/new_skill.py` stamps a test file that already calls them.

The functions take the skill's own paths, so a test file in another repo root (the stamper's test) can use them too.
A change here is NOT in the fingerprint of a skill (`skill_gates.fingerprint` hashes the skill, its QA file and its own
test file); after a change run `python -m pytest tests -q` and, for the live tests, `python tests/live_proof.py`.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

import pytest

from skill_gates import live  # noqa: F401  (one definition of the live mark; test files import it from here too)

TOOLS = Path(__file__).resolve().parent.parent / "tools"


def run_script(script: Path, *args: str, cwd: Path | None = None, env: dict | None = None) -> subprocess.CompletedProcess[str]:
    """Start a skill script as a real subprocess with stdin closed (headless: no prompts)."""
    return subprocess.run([sys.executable, str(script), *args], capture_output=True, text=True, encoding="utf-8", errors="replace",
                          stdin=subprocess.DEVNULL, timeout=60, cwd=cwd, env=env)


def help_runs(script: Path, *flags: str) -> None:
    """Stock test 1: `--help` exits 0 without a prompt and names every flag."""
    r = run_script(script, "--help")
    assert r.returncode == 0 and all(flag in r.stdout for flag in flags), r.stdout + r.stderr


def skill_md_documents(skill: Path, needles: Iterable[str], *refs: str) -> None:
    """Stock test 2: SKILL.md (plus the named references/ files) holds each line the script prints, as written."""
    text = (skill / "SKILL.md").read_text(encoding="utf-8") + "".join((skill / ref).read_text(encoding="utf-8") for ref in refs)
    for needle in needles:
        assert needle in text, needle


class Installed:
    """A copy of a skill installed like another repo does, and a runner that starts its script through pwsh."""

    def __init__(self, script: Path, elsewhere: Path, pwsh: str) -> None:
        self.script, self.elsewhere, self.pwsh = script, elsewhere, pwsh

    def run(self, *args: str) -> tuple[int, str]:
        """Run the installed script from `elsewhere` with each arg as a quoted PowerShell string: (exit code, stdout)."""
        quoted = " ".join("'" + a.replace("'", "''") + "'" for a in args)
        cmd = f"& '{sys.executable}' '{self.script}' {quoted}; exit $LASTEXITCODE"
        r = subprocess.run([self.pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", cmd], cwd=self.elsewhere, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=120)
        return r.returncode, r.stdout.strip()

    def assert_nothing_written_elsewhere(self) -> None:
        assert not list(self.elsewhere.iterdir()), "nothing is written next to where it was started"


def installed_copy(tmp_path: Path, name: str, script_rel: str, skills: Path | None = None) -> Installed:
    """Stock test 3, the setup: install the skill with tools/install_fleet_skills.py into `<tmp>/other repo/skills`, check the
    copy matches the source, and return a runner for the installed script. Skips when pwsh 7 is not installed.
    `skills` is the folder that holds the source skill (default: this repo's skills/)."""
    sys.path.insert(0, str(TOOLS))
    import install_fleet_skills as inst
    saved = inst.SKILLS
    if skills is not None:
        inst.SKILLS = skills
    try:
        dest = tmp_path / "other repo" / "skills"
        inst.install(name, dest)
        assert inst.stale(name, dest) == []
    finally:
        inst.SKILLS = saved
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh 7 is not installed")
    return Installed(dest / name / script_rel, elsewhere, pwsh)
