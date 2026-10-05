"""Adoption check for the engine-builder skill (board DR-1004-1).

Reads only: the private adopted.csv, the 48 h loads scan
(tools/fleet_failures.py, database opened read-only) and the frozen
proof skills/engine-builder/references/trial-proof.json. Writes nothing.

    python tools/adopt_engine_builder.py [--status] [--json]
    python tools/adopt_engine_builder.py --help

Prints the 48 h class-halving status for repos that load the skill.
Never re-runs cure trials: lead decision 2026-10-04 says the proof
stands (12 runs, with 1.0 / without 0.4167, lift 0.5833), so any
trial flag is refused instead of run.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fleet_failures as ff  # noqa: E402  (read-only loads scan)

ROOT = HERE.parent
SKILL = "engine-builder"
PROOF = ROOT / "skills" / SKILL / "references" / "trial-proof.json"
DEFAULT_CSV = Path("C:/Users/me/.empire/state/skilldoctor/adopted.csv")
REFUSED = ("--trial", "--rerun", "--re-run", "--cure", "--grade", "--reproof", "--run-trials")


def read_proof() -> dict:
    try:
        return json.loads(PROOF.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def read_rows(path: Path) -> list[list[str]]:
    try:
        return [r for r in csv.reader(path.read_text(encoding="utf-8-sig").splitlines()) if r]
    except OSError:
        return []


def status(csv_path: Path, db_given: str | None) -> tuple[list[str], dict]:
    """Adoption lines plus a machine summary. Read-only: no trials, no writes."""
    proof = read_proof()
    rows = read_rows(csv_path)
    own = [r for r in rows[1:] if len(r) >= 6 and r[2].strip() == SKILL] if rows else []
    lines = []
    if proof.get("ok"):
        lines.append(
            f"proof stands: {proof.get('runs')} runs "
            f"with {proof.get('with_rate')} without {proof.get('without_rate')} "
            f"lift {proof.get('lift')} ({proof.get('sheet')})"
        )
    else:
        lines.append("proof file unreadable: skills/engine-builder/references/trial-proof.json")
    if not rows:
        lines.append(f"no adopted.csv at {csv_path}: adoption pending")
    for r in own:
        after = r[5].strip() or "pending 48 h window"
        lines.append(f"adopted.csv: {r[0].strip()} {r[1].strip()} {r[2].strip()} {r[3].strip()} before {r[4].strip()} after {after}")
    db = ff.resolve_db(db_given)
    if not db.is_file():
        lines.append(f"no opencode.db at {db}: loads scan skipped, adoption pending")
        return lines, {"skill": SKILL, "loads_48h": {}, "verdict": "pending"}
    detail = ff.loads_detail(db, hours=48)
    mine = {repo: n for (name, repo), n in sorted(detail.items()) if name == SKILL}
    if mine:
        lines.append("loads 48 h: " + ", ".join(f"{r} {n}" for r, n in mine.items()))
    else:
        lines.append("loads 48 h: 0 loads of engine-builder in 48 h across 0 repos: adoption pending")
    before = ff.skill_before(SKILL, csv_path)
    now = ff.skill_now(SKILL, db, ff.repo_dirs())
    verdict = ff.verdict_for(SKILL, before, now)
    lines.append(f"class 48 h: before {before} now {now} {verdict}")
    if not any(len(r) >= 6 and r[3].strip().lower() == "adopted" and r[5].strip() for r in own):
        lines.append("class-halving: pending installer adoption plus 48 h window, not measured same-day")
    return lines, {"skill": SKILL, "loads_48h": mine, "before": before, "now": now, "verdict": verdict}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--status", action="store_true", help="print the adoption status (default)")
    ap.add_argument("--json", action="store_true", help="print the summary as one JSON line")
    ap.add_argument("--csv", default=str(DEFAULT_CSV), help="adopted.csv path")
    ap.add_argument("--db", default=None, help="opencode.db path")
    args, unknown = ap.parse_known_args(argv)
    for flag in list(unknown) + list(sys.argv[1:]):
        if flag in REFUSED or flag.startswith("--trial="):
            print("refused: lead decision 2026-10-04: proof stands "
                  "(12 runs 1.0/0.4167 lift 0.5833), no further cure runs before adoption")
            return 2
    lines, summary = status(Path(args.csv), args.db)
    if args.json:
        print(json.dumps(summary, sort_keys=True))
    else:
        for line in lines:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
