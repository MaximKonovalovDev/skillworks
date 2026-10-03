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
and after at most half of it meets the bar.
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
    """Loads of this repo's skills per other repo in the last `hours` (the database is read-only)."""
    skills, own = skills or SKILLS, own or ROOT
    names = _skill_names(skills)
    cutoff = (time.time() * 1000 if now_ms is None else now_ms) - hours * 3_600_000
    con = sqlite3.connect(f"{db.resolve().as_uri()}?mode=ro", uri=True, timeout=30)
    try:
        sessions = dict(con.execute("select id, directory from session where time_updated > ?", (cutoff,)))
        out: dict[str, int] = {}
        for sid, data in con.execute("select session_id, data from part where time_created > ? and data like ?", (cutoff, '%"tool":"skill"%')):
            part = json.loads(data)
            name = ((part.get("state") or {}).get("input") or {}).get("name")
            repo = _repo_of(sessions.get(sid) or "", own) if part.get("tool") == "skill" and name in names else None
            if repo:
                out[repo] = out.get(repo, 0) + 1
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


def s1(db: Path | None = None) -> tuple[bool, str]:
    loads, why = _loads(db)
    if loads is None:
        return False, why
    n = sum(loads.values())
    return n >= LOADS_NEEDED, f"{n} loads of skillworks skills in {HOURS} h by loops outside it (want {LOADS_NEEDED})"


def s2(db: Path | None = None) -> tuple[bool, str]:
    loads, why = _loads(db)
    if loads is None:
        return False, why
    seen = ", ".join(f"{r} {n}" for r, n in sorted(loads.items())) or "none"
    return len(loads) >= REPOS_NEEDED, f"{len(loads)} other repos loaded one in {HOURS} h (want {REPOS_NEEDED}): {seen}"


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


def s5(path: Path = ADOPTED) -> tuple[bool, str]:
    try:
        rows = list(csv.reader(path.read_text(encoding="utf-8-sig").splitlines()))
    except OSError:
        return False, f"no adopted.csv at {path}"
    adopted = [r for r in rows if len(r) >= 6 and r[3].strip().lower() == "adopted" and r[1].strip() != "skillworks"]
    measured, halved = 0, []
    for r in adopted:
        try:
            before, after = float(r[4]), float(r[5])
        except ValueError:
            continue  # no after number yet
        measured += 1
        if before > 0 and after * 2 <= before:
            halved.append(f"{r[1].strip()}/{r[2].strip()} {r[4].strip()} -> {r[5].strip()}")
    return bool(halved), f"{len(halved)} class(es) fell by half (want 1): {', '.join(halved) or 'none'}; {measured} of {len(adopted)} adopted rows have an after number"


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
