"""G-17 promptfoo trial harness (TS-6 eval row context).

Scores evals/g17-trial.yaml by code, stdlib only, offline, no model calls,
no network. The YAML follows the promptfoo pattern (providers before/after
plus prompts plus cases with assertions) in the repo's trial-sheet shape
(id plus kind plus task plus must plus must_not), each case carrying the
frozen before (bare baseline) and after (skill-equipped) fixtures. The
runner grades both arms like tools/skill_trial.py score_task, takes lift
as the mean paired per-task difference with its stderr from the shared
metric in tools/eval_score.py, and exits CI PASS when the sheet holds
12 tasks with with_rate 0.8 or more and lift 0.3 or more.

Commands::

    python tools/g17-promptfoo.py sheet [--yaml <file>]
    python tools/g17-promptfoo.py run [--yaml <file>] [--out <file>]

run writes one JSON proof (default work/g17-promptfoo/g17-trial-proof.json,
kept out of skills/ so fleet live-proof fingerprints never move) and
prints one lift line plus RESULT PASS or RESULT FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_YAML = ROOT / "evals" / "g17-trial.yaml"
DEFAULT_OUT = ROOT / "work" / "g17-promptfoo" / "g17-trial-proof.json"

KINDS = ("run", "answer")


def _scalar(value: str) -> str:
    """Parse one double-quoted or plain scalar from our YAML shape."""
    value = value.strip()
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def _flow_list(value: str) -> list[str]:
    """Parse one flow list like [alpha, 0.5] into strings."""
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return []
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [_scalar(part) for part in inner.split(",")]


def load_yaml(path: Path) -> tuple[dict, list[dict], list[str]]:
    """Read our YAML shape. Returns (meta, cases, problems)."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, [], [f"cannot read {path}: {exc}"]
    meta: dict = {"thresholds": {}}
    cases: list[dict] = []
    problems: list[str] = []
    current: dict | None = None
    section: str | None = None
    for n, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line.startswith("  - id:") and section == "cases":
            current = {"id": _scalar(line.split(":", 1)[1])}
            cases.append(current)
            continue
        if line.startswith("thresholds:"):
            section = "thresholds"
            continue
        if line.startswith("cases:"):
            section = "cases"
            continue
        if not line.startswith(" ") and ":" in line:
            section = "top"
            continue
        if section == "thresholds":
            if ":" not in stripped:
                problems.append(f"{path}:{n}: bad threshold line")
                continue
            key, value = (part.strip() for part in stripped.split(":", 1))
            try:
                meta["thresholds"][key] = float(value)
            except ValueError:
                problems.append(f"{path}:{n}: threshold {key!r} is not a number")
            continue
        if section == "cases" and current is not None and ":" in stripped:
            key, value = (part.strip() for part in stripped.split(":", 1))
            if value.startswith("["):
                current[key] = _flow_list(value)
            else:
                current[key] = _scalar(value)
    meta.setdefault("suite", "g17-trial")
    seen: set[str] = set()
    for case in cases:
        case_id = case.get("id", "?")
        if case_id in seen:
            problems.append(f"{path}: duplicate id {case_id!r}")
        seen.add(case_id)
        if case.get("kind") not in KINDS:
            problems.append(f"{path}: {case_id!r} kind must be run|answer")
        if not isinstance(case.get("task"), str) or not case["task"].strip():
            problems.append(f"{path}: {case_id!r} has no task text")
        for key in ("must", "must_not"):
            if key in case and (
                not isinstance(case[key], list)
                or not all(isinstance(s, str) for s in case[key])
            ):
                problems.append(f"{path}: {case_id!r} {key} must be a list of strings")
        for key in ("before", "after"):
            if not isinstance(case.get(key), str) or not case[key]:
                problems.append(f"{path}: {case_id!r} has no {key} fixture")
    return meta, cases, problems


def score_case(case: dict, text: str) -> tuple[bool, str | None]:
    """Score one fixture by code, the skill_trial rule. Returns (passed, finding)."""
    case_id = case.get("id", "?")
    blob = text or ""
    for word in case.get("must", []) or []:
        if word.lower() not in blob.lower():
            return False, f"{case_id!r} misses {word!r}"
    for word in case.get("must_not", []) or []:
        if word.lower() in blob.lower():
            return False, f"{case_id!r} contains forbidden {word!r}"
    return True, None


def mean_stderr(xs: list[float]) -> tuple[float, float]:
    """Shared metric: mean plus the stderr of the mean (sample std / sqrt(n))."""
    n = len(xs)
    if n == 0:
        return 0.0, 0.0
    mean = sum(xs) / n
    if n == 1:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, math.sqrt(var / n)


def grade(cases: list[dict], thresholds: dict | None = None) -> dict:
    """Grade both arms and take lift as the mean paired difference."""
    limits = {"min_runs": 12, "min_with_rate": 0.8, "min_lift": 0.3}
    limits.update(thresholds or {})
    with_out: dict[str, bool] = {}
    without_out: dict[str, bool] = {}
    findings: list[str] = []
    for case in cases:
        passed, finding = score_case(case, case.get("after", ""))
        with_out[case["id"]] = passed
        if finding:
            findings.append(f"after: {finding}")
        passed, finding = score_case(case, case.get("before", ""))
        without_out[case["id"]] = passed
        if finding:
            findings.append(f"before: {finding}")
    runs = len(cases)
    with_rate = round(sum(1 for c in cases if with_out[c["id"]]) / runs, 4) if runs else 0.0
    without_rate = round(sum(1 for c in cases if without_out[c["id"]]) / runs, 4) if runs else 0.0
    diffs = [
        (1.0 if with_out[c["id"]] else 0.0) - (1.0 if without_out[c["id"]] else 0.0)
        for c in cases
    ]
    lift, lift_stderr = mean_stderr(diffs)
    spread = round(sum(1 for d in diffs if d != 0.0) / runs, 4) if runs else 0.0
    canonical = json.dumps(
        [
            {
                "id": c["id"],
                "kind": c.get("kind"),
                "task": c.get("task"),
                "must": c.get("must", []),
                "must_not": c.get("must_not", []),
                "before": c.get("before"),
                "after": c.get("after"),
            }
            for c in sorted(cases, key=lambda c: c["id"])
        ],
        sort_keys=True,
        ensure_ascii=True,
    )
    ok = (
        runs >= limits["min_runs"]
        and with_rate >= limits["min_with_rate"]
        and round(lift, 4) >= limits["min_lift"]
    )
    return {
        "suite": "g17-trial",
        "runs": runs,
        "with_rate": with_rate,
        "without_rate": without_rate,
        "lift": round(lift, 4),
        "lift_stderr": round(lift_stderr, 4),
        "spread": spread,
        "thresholds": limits,
        "findings": findings,
        "fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "sheet": "evals/g17-trial.yaml",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "ok": ok,
    }


def cmd_sheet(args: argparse.Namespace) -> int:
    _, cases, problems = load_yaml(Path(args.yaml))
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        print("RESULT FAIL")
        return 1
    for case in cases:
        print(f"{case['id']} [{case['kind']}] {case['task']}")
    print(f"tasks {len(cases)}")
    print("RESULT PASS")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    meta, cases, problems = load_yaml(Path(args.yaml))
    for problem in problems:
        print(f"FAIL {problem}")
    if problems or not cases:
        print("RESULT FAIL")
        return 1
    record = grade(cases, meta.get("thresholds"))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"runs {record['runs']}, with_rate {record['with_rate']}, "
          f"without_rate {record['without_rate']}, lift {record['lift']} "
          f"+/- {record['lift_stderr']}")
    print(f"proof {out}")
    print("RESULT PASS" if record["ok"] else "RESULT FAIL")
    return 0 if record["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="G-17 promptfoo trial harness: grade before/after fixtures.")
    sub = parser.add_subparsers(dest="command", required=True)
    sheet = sub.add_parser("sheet", help="print the 12 task prompts a stranger runs cold")
    sheet.add_argument("--yaml", default=str(DEFAULT_YAML), help="trial file (default evals/g17-trial.yaml)")
    sheet.set_defaults(func=cmd_sheet)
    run = sub.add_parser("run", help="score before/after arms and write the proof")
    run.add_argument("--yaml", default=str(DEFAULT_YAML), help="trial file (default evals/g17-trial.yaml)")
    run.add_argument("--out", default=str(DEFAULT_OUT), help="proof path (default work/g17-promptfoo/g17-trial-proof.json)")
    run.set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
