"""Repair 002 re-seal for DR-1004-2 (edit-reread) + DR-1004-4 (edit-unique).

    python tools/repair_edit_pair.py [--out evals/edit-reread_reseal_2026-10-05.json]

Re-grades the sealed 12-task sheets of both skills through
tools/skill_trial.py grade logic (load_sheet + score_arm + summarize)
read-only: it never writes into skills/ (sealed), only the one reseal
JSON given by --out. That JSON carries with_rate, without_rate and
lift per skill so the judge can re-seal without re-running a model.

Offline, no model calls, no network.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import skill_trial as trial  # noqa: E402  (same folder, read-only grade logic)

ROOT = HERE.parent
SKILLS = ("edit-reread", "edit-unique")
DEFAULT_OUT = ROOT / "evals" / "edit-reread_reseal_2026-10-05.json"


def grade_skill(skill: str, evals: Path, trials_root: Path) -> tuple[dict | None, list[str]]:
    """Grade one sealed skill read-only. Returns (record, problems)."""
    tasks, problems = trial.load_sheet(skill, evals)
    with_rows, with_problems = trial._load_jsonl(trials_root / skill / "with.jsonl")
    without_rows, without_problems = trial._load_jsonl(trials_root / skill / "without.jsonl")
    problems = list(problems) + list(with_problems) + list(without_problems)
    if not tasks or with_problems or without_problems:
        return None, problems
    with_out, with_find = trial.score_arm(tasks, with_rows)
    without_out, without_find = trial.score_arm(tasks, without_rows)
    record = trial.summarize(skill, tasks, with_out, without_out)
    return record, problems + [f"with: {f}" for f in with_find] + [f"without: {f}" for f in without_find]


def reseal(evals: Path, trials_root: Path) -> tuple[dict, list[str]]:
    """Grade both sealed skills. Returns (doc, problems). Writes nothing."""
    skills: dict[str, dict] = {}
    problems: list[str] = []
    for skill in SKILLS:
        record, errs = grade_skill(skill, evals, trials_root)
        problems += [f"{skill}: {e}" for e in errs]
        if record is None:
            skills[skill] = {"skill": skill, "runs": 0, "ok": False}
        else:
            skills[skill] = record
    ok = all(s.get("ok") for s in skills.values())
    doc = {
        "repair": "002",
        "rows": ["DR-1004-2", "DR-1004-4"],
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "skills": skills,
        "ok": ok,
    }
    return doc, problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--evals", default=str(ROOT / "evals"))
    ap.add_argument("--trials", default=str(ROOT / "work" / "trials"))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)
    doc, problems = reseal(Path(args.evals), Path(args.trials))
    for skill in SKILLS:
        s = doc["skills"][skill]
        print(f"{skill} runs {s.get('runs')}, with_rate {s.get('with_rate')}, "
              f"without_rate {s.get('without_rate')}, lift {s.get('lift')}")
    for problem in problems:
        print(f"FAIL {problem}")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"proof {out}")
    print("RESULT PASS" if doc["ok"] else "RESULT FAIL")
    return 0 if doc["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
