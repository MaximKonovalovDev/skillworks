"""Adoption push checker for DR-1004-3 (skill repo-read-first).

Maps the 29-misses-a-day class to skill loads, per repo, and prints
the adoption gap: repos that still miss reads but load the skill
zero times. Reads the OpenCode history read-only through
fleet_failures (scan_db for misses, loads_detail for loads, the
same counter as `fleet_failures.py loads`). Writes nothing, edits
no skill.

    python tools/adopt_repo_read_first.py
    python tools/adopt_repo_read_first.py --json
    python tools/adopt_repo_read_first.py --check

--check exits 1 while any repo with misses loads zero times, else 0.
Without --check the exit is 0 so the line can run in any loop.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fleet_failures as ff  # noqa: E402  (read-only scan and loads)

SKILL = "repo-read-first"
HOURS = 48
LOADS_HOURS = 24
# Same class as skills/repo-read-first/references/target-class.json:
# guessed repo reads against the wiki service and the git host.
TOOLS = ("deepwiki_ask_wiki_question", "github_get_file_contents")
ERRORS = ("Repository not found", "does not point to a file", "could not resolve ref")


def misses_by_repo(scan: dict) -> dict[str, int]:
    """48 h guessed-read misses per repo, from a read-only scan."""
    out: dict[str, int] = {}
    for key, val in (scan.get("classes") or {}).items():
        if not key.startswith(TOOLS):
            continue
        if not any(e in key for e in ERRORS):
            continue
        for repo, n in (val.get("repos") or {}).items():
            out[repo] = out.get(repo, 0) + n
    return out


def loads_by_repo(detail: dict) -> dict[str, int]:
    """24 h loads of repo-read-first per repo (same counter as loads)."""
    out: dict[str, int] = {}
    for (skill, repo), n in detail.items():
        if skill == SKILL:
            out[repo] = out.get(repo, 0) + n
    return out


def rows(misses: dict[str, int], loads: dict[str, int]) -> list[dict]:
    """One row per repo with misses, most misses first."""
    out = []
    for repo in sorted(misses, key=lambda r: -misses[r]):
        n_loads = loads.get(repo, 0)
        out.append({"repo": repo, "misses": misses[repo], "loads": n_loads,
                    "gap": n_loads == 0})
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--db", default=None, help="opencode.db path (default OPENCODE_DB or the local share file)")
    ap.add_argument("--hours", type=float, default=HOURS, help="miss window in hours (default 48)")
    ap.add_argument("--loads-hours", type=float, default=LOADS_HOURS, help="load window in hours (default 24)")
    ap.add_argument("--json", action="store_true", help="print one JSON doc instead of lines")
    ap.add_argument("--check", action="store_true", help="exit 1 while any repo with misses has zero loads")
    args = ap.parse_args(argv)
    db = ff.resolve_db(args.db)
    if not db.is_file():
        print(f"no opencode.db at {db}")
        return 1
    scan = ff.scan_db(db, args.hours, ff.repo_dirs())
    misses = misses_by_repo(scan)
    loads = loads_by_repo(ff.loads_detail(db, hours=args.loads_hours))
    data = rows(misses, loads)
    gaps = [r for r in data if r["gap"]]
    if args.json:
        print(json.dumps({"skill": SKILL, "miss_hours": args.hours, "load_hours": args.loads_hours,
                          "misses": sum(misses.values()), "loads": sum(loads.values()),
                          "gap_repos": [r["repo"] for r in gaps], "repos": data}, indent=1))
    else:
        for r in data:
            state = "GAP no loads" if r["gap"] else f"covered {r['loads']} loads"
            print(f"{r['repo']:<17} {r['misses']} misses in {args.hours:g} h, {r['loads']} loads in {args.loads_hours:g} h -> {state}")
        names = ", ".join(r["repo"] for r in gaps) or "none"
        print(f"{SKILL}: {sum(misses.values())} misses in {len(data)} repos, {sum(loads.values())} loads, gap in {len(gaps)} repos: {names}")
    if args.check and gaps:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
