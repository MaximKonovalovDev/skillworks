#!/usr/bin/env python3
"""brooks-law-team: score a team plan for late-staff risk, team shape and design gate.

Headless: no network, no prompts. Reads one JSON plan file from --input,
counts talk channels as n*(n-1)/2, shapes a chief-led team, gates the design
on one holder, and writes report.json plus plan.txt into --out.

Usage:
    python scripts/brooks_law_team.py --input <plan.json> --out <report-dir>

The first word of stdout is the answer. Exit codes: 0 on PLAN or HOLD, 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DESCRIPTION = "Check a team plan for Brooks-law risk before adding people late: count channels, shape a surgical team, gate design integrity. Use when staffing or replanning a late project and deciding whether to add people."


def channels(n: int) -> int:
    """Talk channels for n people: n*(n-1)//2."""
    return n * (n - 1) // 2


def shape(n: int) -> str:
    """Surgical shape in own words: one chief plus support, split over 7."""
    if n <= 7:
        return f"1 chief + {n - 1} support"
    return "1 chief + 6 support, split rest into a second team"


def load_plan(path: Path) -> tuple[dict | None, str | None]:
    """Read and check the plan file. Returns (plan, error)."""
    if not path.is_file():
        return None, f"ERROR input file missing: {path}"
    try:
        text = path.read_bytes().decode("utf-8")
    except OSError as err:
        return None, f"ERROR cannot read input: {err.strerror or err}"
    except UnicodeDecodeError:
        return None, f"ERROR input is not UTF-8 text: {path}"
    try:
        plan = json.loads(text)
    except ValueError:
        return None, f"ERROR input is not valid JSON: {path}"
    if not isinstance(plan, dict):
        return None, f"ERROR input must be a JSON object: {path}"
    return plan, None


def check_plan(plan: dict) -> tuple[dict | None, str | None]:
    """Check plan values. Returns (clean plan, error)."""
    allowed = {"n", "late_add", "weeks_left", "design_owners", "splittable"}
    unknown = sorted(set(plan) - allowed)
    if unknown:
        return None, f"ERROR unknown key: {unknown[0]}"
    for key in ("n", "weeks_left", "design_owners"):
        if key not in plan:
            return None, f"ERROR input misses key: {key}"
    n = plan["n"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        return None, f"ERROR bad n: {n!r}, want int 1 or more"
    late_add = plan.get("late_add", 0)
    if isinstance(late_add, bool) or not isinstance(late_add, int) or late_add < 0:
        return None, f"ERROR bad late_add: {late_add!r}, want int 0 or more"
    weeks_left = plan["weeks_left"]
    if isinstance(weeks_left, bool) or not isinstance(weeks_left, (int, float)) or weeks_left < 0:
        return None, f"ERROR bad weeks_left: {weeks_left!r}, want number 0 or more"
    owners = plan["design_owners"]
    if isinstance(owners, bool) or not isinstance(owners, int) or owners < 1:
        return None, f"ERROR bad design_owners: {owners!r}, want int 1 or more"
    splittable = plan.get("splittable", False)
    if not isinstance(splittable, bool):
        return None, f"ERROR bad splittable: {splittable!r}, want true or false"
    return {"n": n, "late_add": late_add, "weeks_left": weeks_left,
            "design_owners": owners, "splittable": splittable}, None


def score(clean: dict) -> dict:
    """Score the clean plan. Returns the report record."""
    n = clean["n"]
    late_add = clean["late_add"]
    grown = n + late_add
    c = channels(n)
    c2 = channels(grown)
    integrity = "PASS" if clean["design_owners"] <= 2 else "FAIL"
    reasons: list[str] = []
    if late_add > 0 and clean["weeks_left"] <= 6 and not clean["splittable"]:
        reasons.append("late staff on a short clock")
    if grown > 7:
        reasons.append("team over 7 split in two")
    if clean["design_owners"] > 2:
        reasons.append(f"{clean['design_owners']} design owners keep 1 or 2")
    verdict = "HOLD" if reasons else "PLAN"
    return {"tool": "brooks-law-team", "n": n, "late_add": late_add,
            "weeks_left": clean["weeks_left"], "design_owners": clean["design_owners"],
            "splittable": clean["splittable"], "channels": c, "grown_channels": c2,
            "added_channels": c2 - c, "surgical": shape(grown),
            "integrity": integrity, "verdict": verdict, "reasons": reasons}


def answer_line(rep: dict) -> str:
    """The one answer line whose first word is PLAN or HOLD."""
    base = f"{rep['verdict']} n={rep['n']} channels={rep['channels']}"
    if rep["late_add"] > 0:
        base += f" to {rep['grown_channels']}"
    base += f" integrity {rep['integrity']} surgical {rep['surgical']}"
    if rep["verdict"] == "HOLD":
        base += f" reason {'; '.join(rep['reasons'])}"
    return base


def plan_text(rep: dict) -> str:
    """Human-readable plan.txt body."""
    lines = [
        f"verdict: {rep['verdict']}",
        f"team: {rep['n']} people, {rep['channels']} channels",
    ]
    if rep["late_add"] > 0:
        lines.append(f"grown team: {rep['n'] + rep['late_add']} people, "
                     f"{rep['grown_channels']} channels (+{rep['added_channels']} new)")
    lines.append(f"surgical: {rep['surgical']}")
    lines.append(f"integrity: {rep['integrity']} ({rep['design_owners']} owner(s), keep 1 or 2)")
    if rep["reasons"]:
        lines.append("reasons: " + "; ".join(rep["reasons"]))
    else:
        lines.append("reasons: none, team can go as shaped")
    return "\n".join(lines) + "\n"


def work(args: argparse.Namespace) -> int:
    src = Path(args.input)
    out = Path(args.out)
    plan, err = load_plan(src)
    if err is not None:
        print(err)
        return 2
    clean, err = check_plan(plan or {})
    if err is not None:
        print(err)
        return 2
    try:
        same = src.resolve() == out.resolve()
    except OSError:
        same = False
    if same:
        print(f"ERROR refused: --out is the input file: {out}")
        return 2
    if out.is_file() or (out.exists() and not out.is_dir()):
        print(f"ERROR refused: --out is a file: {out}")
        return 2
    rep = score(clean or {})
    try:
        out.mkdir(parents=True, exist_ok=True)
        (out / "report.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8")
        (out / "plan.txt").write_text(plan_text(rep), encoding="utf-8")
    except OSError as exc:
        print(f"ERROR cannot write --out: {exc.strerror or exc}")
        return 2
    print(answer_line(rep))
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="plan JSON file with n, design_owners, weeks_left, optional late_add and splittable")
    parser.add_argument("--out", required=True, help="report dir for report.json plus plan.txt (created on PLAN or HOLD only)")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())
