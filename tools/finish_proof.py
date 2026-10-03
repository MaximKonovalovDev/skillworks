"""Proofs for FINISH-LINE.md bars S2 and S3 (center's finish.mjs runs them as `cmd`; exit 0 = met).

  python tools/finish_proof.py s2 [adopted.csv]   improved skills adopted in 5 of the 9 repos
  python tools/finish_proof.py s3 [skills-dir]    a tested pack has its live store listing URL

S2 reads the skill doctor's record, which lives outside this public repo:
`date,repo,skill,status,no_edit_before,no_edit_after` (status: proposed or adopted).
S3 reads `Live listing: https://...` in skills/<name>/listing.md, written once the factory (or
Maxim) has the pack live, and needs that skill's eval_report.json at or above the 0.6 gate.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ADOPTED = Path("C:/Users/me/.empire/state/skilldoctor/adopted.csv")
SKILLS = Path(__file__).resolve().parent.parent / "skills"
REPOS_NEEDED = 5
GATE = 0.6
LIVE = re.compile(r"^Live listing:\s*(https://\S+)\s*$", re.M)


def s2(path: Path = ADOPTED) -> tuple[bool, str]:
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    except OSError:
        return False, f"no adopted.csv at {path}"
    repos = {r[1].strip() for r in rows if len(r) >= 4 and r[3].strip().lower() == "adopted"}
    return len(repos) >= REPOS_NEEDED, f"{len(repos)} repos adopted a skill (want {REPOS_NEEDED}): {', '.join(sorted(repos)) or 'none'}"


def s3(skills: Path = SKILLS) -> tuple[bool, str]:
    problem = "no listing.md has a 'Live listing: https://...' line yet"
    for listing in sorted(skills.glob("*/listing.md")):
        m = LIVE.search(listing.read_text(encoding="utf-8"))
        if not m:
            continue
        try:
            rate = float(json.loads((listing.parent / "eval_report.json").read_text(encoding="utf-8")).get("rate", 0))
        except (OSError, ValueError):
            rate = 0.0
        if rate >= GATE:
            return True, f"{listing.parent.name} is live at {m.group(1)} (eval {rate:.3f})"
        problem = f"{listing.parent.name} has a live URL but eval {rate:.3f} is below the {GATE} gate"
    return False, problem


def main(argv: list[str]) -> int:
    which = argv[1] if len(argv) > 1 else ""
    if which == "s2":
        ok, msg = s2(Path(argv[2])) if len(argv) > 2 else s2()
    elif which == "s3":
        ok, msg = s3(Path(argv[2])) if len(argv) > 2 else s3()
    else:
        print("usage: python tools/finish_proof.py s2|s3 [path]")
        return 2
    print(("met: " if ok else "open: ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
