"""Run the live tests of the fleet skills and record a proof.

    python tests/live_proof.py                 # every built fleet skill
    python tests/live_proof.py git-one-branch  # one skill

Live tests start real programs (pwsh, git, a browser) and take a minute or more, so the default
`python -m pytest tests/` skips them. Here each skill's test file runs with SKILL_LIVE=1. When every
test passes and none is skipped, skills/<name>/references/live-proof.json stores a fingerprint of the
skill, its QA file and its test file. The default run fails when a skill no longer matches its proof.

Exit code 0 when every named skill is proven.
"""
from __future__ import annotations

import datetime
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))  # book2skill, for skill_gates
import skill_gates as g  # noqa: E402


def versions() -> dict:
    out = {"python": platform.python_version(), "os": platform.platform()}
    for tool, args in (("git", ["--version"]), ("node", ["--version"]), ("pwsh", ["-NoProfile", "-Command", "$PSVersionTable.PSVersion.ToString()"])):
        exe = shutil.which(tool)
        if exe:
            r = subprocess.run([exe, *args], capture_output=True, text=True)
            out[tool] = (r.stdout or r.stderr).strip()
    return out


def same_seal(existing: dict, fingerprint: str, result: str) -> bool:
    """A fresh seal stands: the same fingerprint and the same result line mean a re-run must not rewrite the proof.

    Rewriting would bump the date (and versions text), which re-stales the pack zip hours after a green rebuild.
    A changed skill still fails the fingerprint match below, so the bar does not move."""
    return existing.get("fingerprint") == fingerprint and existing.get("result") == result


def prove(name: str) -> bool:
    test_file = g.test_file_for(name)
    if not (g.SKILLS / name / "SKILL.md").is_file() or not test_file.is_file():
        print(f"{name}: not built (no SKILL.md or no {test_file.name})")
        return False
    env = dict(os.environ, SKILL_LIVE="1")
    r = subprocess.run([sys.executable, "-m", "pytest", str(test_file), "-q", "-p", "no:cacheprovider"], cwd=g.ROOT, env=env, capture_output=True, text=True)
    tail = (r.stdout.strip().splitlines() or [""])[-1]
    skipped = re.search(r"(\d+) skipped", tail)
    if r.returncode != 0 or skipped:
        print(f"{name}: NOT proven. {tail}")
        print("\n".join(r.stdout.strip().splitlines()[-25:]))
        return False
    fingerprint = g.fingerprint(name)
    proof_path = g.SKILLS / name / "references" / g.PROOF_NAME
    if proof_path.is_file():
        try:
            existing = json.loads(proof_path.read_text(encoding="utf-8"))
        except ValueError:
            existing = {}
        if same_seal(existing, fingerprint, tail):
            print(f"{name}: still proven. {tail}")
            return True
    proof = {
        "skill": name,
        "fingerprint": fingerprint,
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "command": f"SKILL_LIVE=1 python -m pytest tests/{test_file.name} -q",
        "result": tail,
        "versions": versions(),
    }
    (g.SKILLS / name / "references" / g.PROOF_NAME).write_text(json.dumps(proof, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{name}: proven. {tail}")
    return True

def main(argv: list[str]) -> int:
    names = argv or sorted(g.FLEET_SKILLS)
    unknown = [n for n in names if n not in g.FLEET_SKILLS]
    if unknown:
        print(f"unknown skill {unknown}; known: {sorted(g.FLEET_SKILLS)}")
        return 2
    results = [prove(n) for n in names]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
