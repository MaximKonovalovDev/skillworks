"""DR-1005-7 RED baseline plus trials registry: S5 proof is a query.

A RED run is the baseline without the skill (it fails first, on purpose).
A GREEN run is the same count with the skill. Every run is numbered and
carries the change since the last run, so the history can resume.

    python tools/red_baseline_registry.py record --repo forge --skill pwsh-for-bash-writers --phase red --failures 9 --change "before install"
    python tools/red_baseline_registry.py record --repo forge --skill pwsh-for-bash-writers --phase green --failures 4 --change "installed v2"
    python tools/red_baseline_registry.py query [--registry evals/red_baseline_registry.jsonl]
    python tools/red_baseline_registry.py log [--registry ...]
    python tools/red_baseline_registry.py trial-check --skill <name> [--trials work/trials/<name>]

A green run needs an older red run for the same repo and skill: no
baseline, no proof. query prints the first real before-to-after halving
(before above 0, after at most half) and exits 0; else it prints open
and exits 1. trial-check asks for the red arm in trial form:
work/trials/<skill>/without.jsonl with at least one row.

Ideas only from obra/superpowers (MIT: RED baseline fail before writing)
and MaximeRobeyns/self_improving (MIT: numbered run dirs with resume);
no donor code is copied. Offline, no model calls, no network.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_REGISTRY = ROOT / "evals" / "red_baseline_registry.jsonl"
PHASES = ("red", "green")


def load(registry: Path) -> list[dict]:
    """Read the run registry; bad lines are skipped, never fatal."""
    try:
        text = registry.read_text(encoding="utf-8")
    except OSError:
        return []
    runs: list[dict] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            continue
        if isinstance(obj, dict) and obj.get("run"):
            runs.append(obj)
    runs.sort(key=lambda r: str(r["run"]))
    return runs


def next_run(runs: list[dict]) -> str:
    """Next run number (001, 002, ...)."""
    nums = [int(r["run"]) for r in runs if str(r.get("run", "")).isdigit()]
    return f"{(max(nums) + 1) if nums else 1:03d}"


def record(registry: Path, repo: str, skill: str, phase: str,
           failures: int, shells: int = 0, change: str = "",
           at: str | None = None) -> dict:
    """Append one numbered run. Green needs an older red run first."""
    if phase not in PHASES:
        raise ValueError(f"phase must be red|green, got {phase!r}")
    if not repo.strip() or not skill.strip():
        raise ValueError("repo and skill are required")
    if failures < 0 or shells < 0:
        raise ValueError("failures and shells count up from 0")
    runs = load(registry)
    if phase == "green" and not [r for r in runs
                                 if r.get("repo") == repo and r.get("skill") == skill
                                 and r.get("phase") == "red"]:
        raise ValueError(f"no red baseline for {repo}/{skill}: record a red run first")
    entry = {
        "run": next_run(runs),
        "at": at or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "repo": repo,
        "skill": skill,
        "phase": phase,
        "failures": failures,
        "shells": shells,
        "change": change,
    }
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry


def pairs(runs: list[dict]) -> list[dict]:
    """One before/after pair per repo+skill: first red, then first later green."""
    out: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for red in [r for r in runs if r.get("phase") == "red"]:
        key = (str(red.get("repo")), str(red.get("skill")))
        if key in seen:
            continue
        seen.add(key)
        green = next((r for r in runs if r.get("phase") == "green"
                      and r.get("repo") == key[0] and r.get("skill") == key[1]
                      and str(r.get("run", "")) > str(red.get("run", ""))), None)
        if green is not None:
            out.append({"repo": key[0], "skill": key[1],
                        "before": int(red.get("failures", 0)),
                        "after": int(green.get("failures", 0)),
                        "red_run": str(red.get("run")), "green_run": str(green.get("run")),
                        "change": str(green.get("change", ""))})
    return out


def first_halving(runs: list[dict]) -> dict | None:
    """First pair with before above 0 and after at most half."""
    for p in pairs(runs):
        if p["before"] > 0 and p["after"] * 2 <= p["before"]:
            return p
    return None


def query(registry: Path = DEFAULT_REGISTRY) -> tuple[bool, str]:
    """S5 proof as a query over the registry."""
    runs = load(registry)
    found = first_halving(runs)
    if found:
        return True, (f"{len([p for p in pairs(runs) if p['before'] > 0 and p['after'] * 2 <= p['before']])} "
                      f"class(es) fell by half (want 1): {found['repo']}/{found['skill']} "
                      f"{found['before']} -> {found['after']} (runs {found['red_run']}->{found['green_run']})")
    done = len(pairs(runs))
    return False, f"open: no halving yet; {done} paired run(s) in {len(runs)} runs"


def trial_check(skill: str, trials: Path | None = None) -> tuple[bool, str]:
    """The red baseline in trial form: work/trials/<skill>/without.jsonl exists."""
    path = (trials or ROOT / "work" / "trials" / skill) / "without.jsonl"
    try:
        rows = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError as exc:
        return False, f"no red baseline: cannot read {path}: {exc}"
    if not rows:
        return False, f"no red baseline: {path} is empty, run the without-skill arm first"
    return True, f"red baseline: {len(rows)} without-skill run(s) in {path}"


def cmd_record(a: argparse.Namespace) -> int:
    try:
        entry = record(Path(a.registry), a.repo, a.skill, a.phase,
                       a.failures, a.shells, a.change, a.at)
    except ValueError as exc:
        print(f"refused: {exc}")
        return 1
    print(f"run {entry['run']} {entry['repo']}/{entry['skill']} {entry['phase']} failures {entry['failures']}")
    return 0


def cmd_log(a: argparse.Namespace) -> int:
    for r in load(Path(a.registry)):
        print(f"{r.get('run')} {r.get('at')} {r.get('repo')}/{r.get('skill')} "
              f"{r.get('phase')} failures {r.get('failures')}: {r.get('change', '')}")
    return 0


def cmd_query(a: argparse.Namespace) -> int:
    ok, msg = query(Path(a.registry))
    print(("met: " if ok else "") + msg)
    return 0 if ok else 1


def cmd_trial_check(a: argparse.Namespace) -> int:
    ok, msg = trial_check(a.skill, Path(a.trials) if a.trials else None)
    print(msg)
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("record", help="append one numbered red or green run")
    p.add_argument("--repo", required=True)
    p.add_argument("--skill", required=True)
    p.add_argument("--phase", required=True, choices=PHASES)
    p.add_argument("--failures", required=True, type=int)
    p.add_argument("--shells", default=0, type=int)
    p.add_argument("--change", default="")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    p.add_argument("--at", default=None)
    p.set_defaults(fn=cmd_record)
    p = sub.add_parser("log", help="print the change log (one line per run)")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    p.set_defaults(fn=cmd_log)
    p = sub.add_parser("query", help="print the first real before-to-after halving")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    p.set_defaults(fn=cmd_query)
    p = sub.add_parser("trial-check", help="ask for the red arm in trial form")
    p.add_argument("--skill", required=True)
    p.add_argument("--trials", default=None)
    p.set_defaults(fn=cmd_trial_check)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
