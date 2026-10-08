"""Proofs for the FINISH-LINE.md bars (center's finish.mjs runs them as `cmd`; exit 0 = met).

  python tools/finish_proof.py s1 [opencode.db]    10 loads of this repo's skills in 24 h by loops outside this repo
  python tools/finish_proof.py s2 [opencode.db]    those loads come from 5 of the other repos
  python tools/finish_proof.py s3 [skills-dir]     a tested pack has its live store listing URL
  python tools/finish_proof.py s5 [adopted.csv]    a failure class fell by half after a skill was installed
  python tools/finish_proof.py s6 [skills-dir]     8 skills proven (a current live proof, or a trial with lift)

S1 and S2 count real use, not installs: a `skill` tool call in the OpenCode session history (the
database is opened read-only) whose session ran in another git repo and named a skill of this repo.
S3 reads `Live listing: https://...` in skills/<name>/listing.md or packs/<slug>/listing.md, written
once the factory (or Maxim) has the pack live. A skill needs its eval_report.json at or above the 0.6
gate; a pack needs `python tools/pack_check.py packs/<slug>` to end RESULT PASS (that tool lands with
the tool sprint, so until then no pack counts as tested).
S5 reads the skill doctor's record, which lives outside this public repo:
`date,repo,skill,status,before,after` (status: proposed or adopted; before and after are the failure
class counts of the 48 h before and the 48 h after the install). One adopted row with before above 0
and after at most half of it meets the bar. Rows of the skills in UP_IS_GOOD count use, where up is good, and never
meet it. The `after` numbers are measured by tools/adopted_after.py (called here for the real record when a row is due,
and only from a window in which the repo's loop really ran).
S6 counts skills whose live proof is current (tests/skill_gates.check_proof) or whose
references/trial-proof.json holds `runs` 10 or more, `with_rate` 0.8 or more and `lift` 0.3 or more.
"""
from __future__ import annotations

import csv
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ADOPTED = Path("C:/Users/me/.empire/state/skilldoctor/adopted.csv")
SKILLS = ROOT / "skills"
PACK_CHECK = HERE / "pack_check.py"
HOURS = 24
LOADS_NEEDED = 10
REPOS_NEEDED = 5
PROVEN_NEEDED = 8
GATE = 0.6
LIVE = re.compile(r"^Live listing:\s*(https://\S+)\s*$", re.M)
# Skills whose adopted rows count USE, not failures (adopted.csv README: up is good). A fall of those is not a cured class.
UP_IS_GOOD = frozenset({"real-browser-automation", "bevy-rust-ecs"})


def _db_path(given: Path | None) -> Path:
    return given or Path(os.environ.get("OPENCODE_DB") or Path.home() / ".local" / "share" / "opencode" / "opencode.db")


def _skill_names(skills: Path) -> set[str]:
    return {p.name for p in skills.iterdir() if (p / "SKILL.md").is_file() and not p.name.startswith("_")} if skills.is_dir() else set()


def _repo_of(directory: str, own: Path) -> str | None:
    """The git repo a session ran in (loops start at the repo root); None for this repo or a folder that is no repo."""
    here = Path(directory) if directory else None
    if here is None or not (here / ".git").exists():
        return None
    return None if here.resolve() == own.resolve() else here.name


def skill_loads(db: Path, hours: float = HOURS, now_ms: float | None = None, skills: Path | None = None, own: Path | None = None) -> dict[str, int]:
    """Loads of this repo's skills per other repo in the last `hours` (the database is read-only).

    Fast on a multi-GB history: SQLite extracts only the skill name per skill
    part (no full `data` blob crosses into Python, no json.loads per row), the
    same filters as before (a `skill` tool call naming a skill of this repo,
    in a session that ran in another repo)."""
    detail = skill_loads_detail(db, hours=hours, now_ms=now_ms, skills=skills, own=own)
    out: dict[str, int] = {}
    for (_name, repo), n in detail.items():
        out[repo] = out.get(repo, 0) + n
    return out


def skill_loads_detail(db: Path, hours: float = HOURS, now_ms: float | None = None,
                       from_ms: float | None = None, to_ms: float | None = None,
                       skills: Path | None = None, own: Path | None = None) -> dict[tuple[str, str], int]:
    """Skill loads by (skill, repo): the one counter S1/S2 and `fleet_failures loads` share.

    Default is the trailing `hours`. Pass `from_ms`/`to_ms` to count an exact
    window (e.g. one day). See skill_loads for the filters and the speed note."""
    skills, own = skills or SKILLS, own or ROOT
    names = _skill_names(skills)
    if from_ms is not None:
        lo, hi = from_ms, to_ms
    else:
        lo = (time.time() * 1000 if now_ms is None else now_ms) - hours * 3_600_000
        hi = None
    con = sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True, timeout=30)
    try:
        if hi is None:
            sessions = dict(con.execute("select id, directory from session where time_updated > ?", (lo,)))
            q = ("select session_id, json_extract(data,'$.state.input.name') from part "
                 "where time_created > ? and json_extract(data,'$.type')='tool' "
                 "and json_extract(data,'$.tool')='skill'")
            args = (lo,)
        else:
            sessions = dict(con.execute(
                "select id, directory from session where time_updated > ? and time_updated <= ?", (lo, hi)))
            q = ("select session_id, json_extract(data,'$.state.input.name') from part "
                 "where time_created > ? and time_created <= ? and json_extract(data,'$.type')='tool' "
                 "and json_extract(data,'$.tool')='skill'")
            args = (lo, hi)
        out: dict[tuple[str, str], int] = {}
        for sid, name in con.execute(q, args):
            if name in names:
                repo = _repo_of(sessions.get(sid) or "", own)
                if repo and name:
                    out[(name, repo)] = out.get((name, repo), 0) + 1
        return out
    finally:
        con.close()


def _loads(db: Path | None) -> tuple[dict[str, int] | None, str]:
    path = _db_path(db)
    if not path.is_file():
        return None, f"no opencode.db at {path}"
    try:
        return skill_loads(path), ""
    except (sqlite3.Error, ValueError) as err:
        return None, f"cannot read {path}: {err}"


def _breadth(db: Path | None) -> tuple[dict[str, int] | None, str, bool]:
    """Per-repo loads for the S1/S2 path: cached meter reads when fresh, else one scan.

    The default database reads through adopted_after.cached_skill_loads (the shared S1/S2
    meter-read cache, the S5 record-first pattern: met with no scan when proven, refresh
    only while open). A file given on the command line or by a test is scanned as it is,
    never from the cache. Counting always stays in skill_loads, so the bar meaning
    (10 loads in 24 h by loops outside this repo) cannot drift. Returns (loads, why, cached)."""
    if db is None:
        try:
            import adopted_after
            loads, cached = adopted_after.cached_skill_loads()
            if loads is None:
                return None, f"no opencode.db at {_db_path(None)}", False
            return loads, "", cached
        except Exception:
            pass  # a cache fault never breaks the bar: fall through to a direct scan
    loads, why = _loads(db)
    return loads, why, False


def s1(db: Path | None = None) -> tuple[bool, str]:
    loads, why, cached = _breadth(db)
    if loads is None:
        return False, why
    n = sum(loads.values())
    tail = " (already met, no re-scan)" if cached and n >= LOADS_NEEDED else \
        " (cached meter reads)" if cached else ""
    return n >= LOADS_NEEDED, f"{n} loads of skillworks skills in {HOURS} h by loops outside it (want {LOADS_NEEDED}){tail}"


def s2(db: Path | None = None) -> tuple[bool, str]:
    loads, why, cached = _breadth(db)
    if loads is None:
        return False, why
    tail = " (already met, no re-scan)" if cached and len(loads) >= REPOS_NEEDED else \
        " (cached meter reads)" if cached else ""
    seen = ", ".join(f"{r} {n}" for r, n in sorted(loads.items())) or "none"
    return len(loads) >= REPOS_NEEDED, f"{len(loads)} other repos loaded one in {HOURS} h (want {REPOS_NEEDED}): {seen}{tail}"


def _pack_tested(pack: Path) -> tuple[bool, str]:
    if not PACK_CHECK.is_file():
        return False, "tools/pack_check.py has not landed yet"
    r = subprocess.run([sys.executable, str(PACK_CHECK), str(pack)], capture_output=True, text=True, timeout=100)
    return r.returncode == 0 and "RESULT PASS" in r.stdout, f"pack_check says: {(r.stdout.strip().splitlines() or ['nothing'])[-1]}"


def s3(skills: Path = SKILLS, packs: Path | None = None) -> tuple[bool, str]:
    problem = "no listing.md has a 'Live listing: https://...' line yet"
    for listing in [*sorted(skills.glob("*/listing.md")), *sorted((packs or skills.parent / "packs").glob("*/listing.md"))]:
        m = LIVE.search(listing.read_text(encoding="utf-8"))
        if not m:
            continue
        if listing.parent.parent.name == "packs":
            tested, said = _pack_tested(listing.parent)
            if tested:
                return True, f"pack {listing.parent.name} is live at {m.group(1)} ({said})"
            problem = f"pack {listing.parent.name} has a live URL but is not tested: {said}"
            continue
        try:
            rate = float(json.loads((listing.parent / "eval_report.json").read_text(encoding="utf-8")).get("rate", 0))
        except (OSError, ValueError):
            rate = 0.0
        if rate >= GATE:
            return True, f"{listing.parent.name} is live at {m.group(1)} (eval {rate:.3f})"
        problem = f"{listing.parent.name} has a live URL but eval {rate:.3f} is below the {GATE} gate"
    return False, problem


def _halved(rows: list[list[str]]) -> tuple[list[list[str]], int, list[str]]:
    """The adopted rows (outside this repo), how many have an after number, and the halved classes."""
    adopted = [r for r in rows if len(r) >= 6 and r[3].strip().lower() == "adopted" and r[1].strip() != "skillworks"]
    measured, halved = 0, []
    for r in adopted:
        try:
            before, after = float(r[4]), float(r[5])
        except ValueError:
            continue  # no after number yet
        measured += 1
        if r[2].strip() in UP_IS_GOOD:
            continue  # these rows count use, where more is good: a fall is no cured failure
        if before > 0 and after * 2 <= before:
            halved.append(f"{r[1].strip()}/{r[2].strip()} {r[4].strip()} -> {r[5].strip()}")
    return adopted, measured, halved


def s5(path: Path = ADOPTED, refresh: bool | None = None) -> tuple[bool, str]:
    """A failure class fell by half. The `after` numbers are measured here when due (tools/adopted_after.py),
    for the real record only, and only when the record does not already name a halved class: a record that
    already proves the bar is returned met with no database scan, so the proof answers in under a second
    on a multi-GB history instead of timing out. A file given on the command line or by a test is read as it is."""
    note = ""
    if refresh is None:
        refresh = path == ADOPTED
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    except OSError:
        return False, f"no adopted.csv at {path}"
    adopted, measured, halved = _halved(rows)
    if halved:
        return True, (f"{len(halved)} class(es) fell by half (want 1): {', '.join(halved)}; "
                      f"{measured} of {len(adopted)} adopted rows have an after number (already met, no re-scan)")
    if refresh:
        try:
            import adopted_after
            _, said = adopted_after.refresh(path, log=path.parent / "after-log.jsonl")
            note = f"; {said}"
        except Exception as err:  # the bar must still print: a measuring fault is shown, never hidden
            note = f"; after-number measuring failed: {type(err).__name__}: {err}"
        try:
            rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
        except OSError:
            return False, f"no adopted.csv at {path}{note}"
        adopted, measured, halved = _halved(rows)
    return bool(halved), (f"{len(halved)} class(es) fell by half (want 1): {', '.join(halved) or 'none'}; "
                          f"{measured} of {len(adopted)} adopted rows have an after number{note}")


def _live_current(name: str) -> bool:
    """The skill still matches the fingerprint of its last live proof (tests/skill_gates.check_proof)."""
    sys.path[:0] = [str(ROOT / "tests"), str(ROOT)]
    try:
        import skill_gates
        skill_gates.check_proof(name)
        return True
    except (AssertionError, ImportError, OSError, ValueError):
        return False


def _trial_passes(folder: Path) -> bool:
    try:
        t = json.loads((folder / "trial-proof.json").read_text(encoding="utf-8"))
        return t.get("runs", 0) >= 10 and t.get("with_rate", 0) >= 0.8 and t.get("lift", 0) >= 0.3
    except (OSError, ValueError, AttributeError, TypeError):
        return False


def s6(skills: Path = SKILLS, live_ok: Callable[[str], bool] = _live_current) -> tuple[bool, str]:
    names = sorted(_skill_names(skills))
    proven = [n for n in names if _trial_passes(skills / n / "references") or live_ok(n)]
    return len(proven) >= PROVEN_NEEDED, f"{len(proven)} of {len(names)} skills proven (want {PROVEN_NEEDED}): {', '.join(proven) or 'none'}"


BARS = {"s1": s1, "s2": s2, "s3": s3, "s5": s5, "s6": s6}


def main(argv: list[str]) -> int:
    which = argv[1] if len(argv) > 1 else ""
    if which not in BARS:
        print(f"usage: python tools/finish_proof.py {'|'.join(BARS)} [path]")
        return 2
    ok, msg = BARS[which](Path(argv[2])) if len(argv) > 2 else BARS[which]()
    print(("met: " if ok else "open: ") + msg)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
