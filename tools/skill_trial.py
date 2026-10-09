"""Skill trial runner: the stranger-run gate (TS-3, R2 honest eval gate).

    python tools/skill_trial.py sheet --skill <name>
    python tools/skill_trial.py grade --skill <name> [--trials work/trials/<name>]

sheet prints the task sheet from evals/<name>_trials.jsonl (task text only,
never the grading keys) so a stranger can run it cold. grade scores the two
arms of that run -- work/trials/<name>/with.jsonl (skill-equipped) and
without.jsonl (bare baseline) -- by code only: `must` substrings present,
`must_not` substrings absent, and a `run` task is refused when its answer
carries no run output. It writes skills/<name>/references/trial-proof.json
with the keys runs, with_rate, without_rate, lift, spread and fingerprint,
which finish bar S6 reads (runs 10 or more, with_rate 0.8 or more,
lift 0.3 or more).

Ideas only from ai-evos/agent-skills shared/eval_framework.py (Apache-2.0:
skill-equipped versus bare baseline runs, lift between them) and
anthropics/skills skill-creator scripts/aggregate_benchmark.py (Apache-2.0:
with_skill/without_skill run layouts aggregated into one summary); no donor
code is copied. Offline, no model calls, no network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

MIN_RUNS = 10
MIN_WITH_RATE = 0.8
MIN_LIFT = 0.3

KINDS = ("run", "answer")


def _load_jsonl(path: Path) -> tuple[list[dict], list[str]]:
    """Read a JSONL file; returns (rows, problems). One JSON object per line."""
    rows: list[dict] = []
    problems: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"cannot read {path}: {exc}"]
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except ValueError as exc:
            problems.append(f"{path}:{n}: bad JSON: {exc}")
            continue
        if not isinstance(obj, dict):
            problems.append(f"{path}:{n}: not an object")
            continue
        rows.append(obj)
    return rows, problems


def load_sheet(skill: str, evals: Path | None = None) -> tuple[list[dict], list[str]]:
    """Validate the task sheet; returns (tasks, problems)."""
    path = (evals or ROOT / "evals") / f"{skill}_trials.jsonl"
    rows, problems = _load_jsonl(path)
    if problems and not rows:
        return [], problems
    seen: set[str] = set()
    for n, row in enumerate(rows, 1):
        task_id = row.get("id")
        if not isinstance(task_id, str) or not task_id:
            problems.append(f"{path}:{n}: task without an id")
            continue
        if task_id in seen:
            problems.append(f"{path}:{n}: duplicate id {task_id!r}")
        seen.add(task_id)
        if row.get("kind") not in KINDS:
            problems.append(f"{path}:{n}: {task_id!r} kind must be run|answer")
        if not isinstance(row.get("task"), str) or not row["task"].strip():
            problems.append(f"{path}:{n}: {task_id!r} has no task text")
        for key in ("must", "must_not"):
            if key in row and (
                not isinstance(row[key], list)
                or not all(isinstance(s, str) and s for s in row[key])
            ):
                problems.append(f"{path}:{n}: {task_id!r} {key} must be a list of strings")
        if "exit" in row and (not isinstance(row["exit"], int) or isinstance(row["exit"], bool)):
            problems.append(f"{path}:{n}: {task_id!r} exit must be an integer")
    return rows, problems


# Donor: ziyan-wang98/BazaarBench arXiv 2610.06748 (Apache-2.0,
# https://github.com/ziyan-wang98/BazaarBench/blob/main/bazaar/metrics/core.py):
# Pure SQLite Python no LLM no network compute_metrics from state tables,
# MetricsSummary pcr mean median p10 ported fresh binary scores.
# per-task scores with median and worst-decile p10 no donor code copied.
def _median(xs):
    # Median of per-task scores empty gives 0.
    if not xs:
        return 0.0
    ordered = sorted(xs)
    n = len(ordered)
    mid = n // 2
    if n % 2 == 1:
        return round(float(ordered[mid]), 4)
    return round(float((ordered[mid - 1] + ordered[mid]) / 2), 4)


def _p10(xs):
    # Worst decile tenth percentile nearest rank empty gives 0.
    if not xs:
        return 0.0
    ordered = sorted(xs)
    n = len(ordered)
    rank = (n + 9) // 10 - 1
    rank = max(0, min(rank, n - 1))
    return round(float(ordered[rank]), 4)


def check_record(run, want_exit=0, task_id="?"):
    # Grade one run record by exit and output presence.
    if not isinstance(run, dict) or not str(run.get("output", "") or "").strip():
        return False, "refused: run task " + repr(task_id) + " has no run output"
    if run.get("exit") != want_exit:
        return False, repr(task_id) + " run exit " + repr(run.get("exit")) + " != " + str(want_exit)
    return True, None


def score_task(task: dict, answer: dict | None) -> tuple[bool, str | None]:
    """Score one task by code. Returns (passed, finding)."""
    task_id = task.get("id", "?")
    if answer is None:
        return False, f"no answer for {task_id!r}"
    text = str(answer.get("answer", "") or "")
    run = answer.get("run")
    combined = text
    if isinstance(run, dict):
        combined += "\n" + str(run.get("output", "") or "")
    for word in task.get("must", []) or []:
        if word.lower() not in combined.lower():
            return False, f"{task_id!r} misses {word!r}"
    for word in task.get("must_not", []) or []:
        if word.lower() in combined.lower():
            return False, f"{task_id!r} contains forbidden {word!r}"
    if task.get("kind") == "run":
        return check_record(run, task.get("exit", 0), task_id)
    return True, None


def score_arm(tasks: list[dict], answers: list[dict]) -> tuple[dict[str, bool], list[str]]:
    """Score every sheet task against one arm's answers. Returns (outcome by id, findings)."""
    by_id = {a.get("id"): a for a in answers if isinstance(a.get("id"), str)}
    outcomes: dict[str, bool] = {}
    findings: list[str] = []
    for task in tasks:
        passed, finding = score_task(task, by_id.get(task.get("id", "")))
        outcomes[task["id"]] = passed
        if finding:
            findings.append(finding)
    return outcomes, findings


def _trial_rates(tasks, with_out, without_out):
    runs = len(tasks)
    with_rate = round(sum(1 for t in tasks if with_out[t["id"]]) / runs, 4) if runs else 0.0
    without_rate = round(sum(1 for t in tasks if without_out[t["id"]]) / runs, 4) if runs else 0.0
    lift = round(with_rate - without_rate, 4)
    spread = round(
        sum(1 for t in tasks if with_out[t["id"]] != without_out[t["id"]]) / runs, 4
    ) if runs else 0.0
    return runs, with_rate, without_rate, lift, spread


def summarize(skill: str, tasks: list[dict], with_out: dict[str, bool],
              without_out: dict[str, bool]) -> dict:
    """Aggregate the two arms into the trial-proof record."""
    runs, with_rate, without_rate, lift, spread = _trial_rates(tasks, with_out, without_out)
    with_scores = [1.0 if with_out[t["id"]] else 0.0 for t in tasks]
    without_scores = [1.0 if without_out[t["id"]] else 0.0 for t in tasks]
    with_median = _median(with_scores)
    with_p10 = _p10(with_scores)
    without_median = _median(without_scores)
    without_p10 = _p10(without_scores)
    canonical = json.dumps(
        [
            {
                "id": t["id"],
                "kind": t.get("kind"),
                "task": t.get("task"),
                "must": t.get("must", []),
                "must_not": t.get("must_not", []),
                "exit": t.get("exit", 0),
            }
            for t in sorted(tasks, key=lambda t: t["id"])
        ],
        sort_keys=True,
        ensure_ascii=True,
    )
    fingerprint = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    ok = runs >= MIN_RUNS and with_rate >= MIN_WITH_RATE and lift >= MIN_LIFT
    return {
        "skill": skill,
        "runs": runs,
        "with_rate": with_rate,
        "without_rate": without_rate,
        "lift": lift,
        "spread": spread,
        "with_median": with_median,
        "with_p10": with_p10,
        "without_median": without_median,
        "without_p10": without_p10,
        "fingerprint": fingerprint,
        "sheet": f"evals/{skill}_trials.jsonl",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "ok": ok,
    }


# Donor: syrupy-project/syrupy@7dc8f88 (MIT,
# https://raw.githubusercontent.com/syrupy-project/syrupy/7dc8f88a0b039467f808d40b9ccbf7b93488af69/src/syrupy/extensions/single_file.py):
# SingleFileSnapshotExtension keeps one verbatim golden file per snapshot and
# only rewrites it under --snapshot-update; ported fresh here as a frozen
# runs/with_rate/lift golden compare for trial proofs, no donor code copied.
GOLDEN_FIELDS = ("runs", "with_rate", "lift")
GOLDEN_ENV = "SKILL_TRIAL_UPDATE_GOLDEN"


def golden_view(record):
    return {key: record.get(key) for key in GOLDEN_FIELDS}


def check_trial_golden(record, golden_path, update=False):
    path = Path(golden_path)
    want_update = bool(update) or os.environ.get(GOLDEN_ENV, "") in ("1", "true", "yes")
    view = golden_view(record)
    if want_update:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(view, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return True, None
    try:
        golden = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return False, "no golden " + str(path) + ": rerun with --update-golden to create it"
    except (OSError, ValueError) as exc:
        return False, "unreadable golden " + str(path) + ": " + str(exc)
    if not isinstance(golden, dict):
        return False, "unreadable golden " + str(path) + ": not an object"
    for key in GOLDEN_FIELDS:
        if golden.get(key) != view.get(key):
            return False, "golden drift " + str(key) + ": golden " + repr(golden.get(key)) + " != proof " + repr(view.get(key)) + " (rerun with --update-golden to refresh)"
    return True, None


def cmd_sheet(args: argparse.Namespace) -> int:
    tasks, problems = load_sheet(args.skill, Path(args.evals) if args.evals else None)
    for problem in problems:
        print(f"FAIL {problem}")
    if problems:
        print("RESULT FAIL")
        return 1
    for task in tasks:
        print(f"{task['id']} [{task['kind']}] {task['task']}")
    n_run = sum(1 for t in tasks if t["kind"] == "run")
    print(f"tasks {len(tasks)} (run {n_run}, answer {len(tasks) - n_run})")
    print("RESULT PASS")
    return 0


def cmd_grade(args: argparse.Namespace) -> int:
    skill = args.skill
    tasks, problems = load_sheet(skill, Path(args.evals) if args.evals else None)
    trials = Path(args.trials) if args.trials else ROOT / "work" / "trials" / skill
    with_rows, with_problems = _load_jsonl(trials / "with.jsonl")
    without_rows, without_problems = _load_jsonl(trials / "without.jsonl")
    problems += with_problems + without_problems
    for problem in problems:
        print(f"FAIL {problem}")
    if not tasks or with_problems or without_problems:
        print("RESULT FAIL")
        return 1
    with_out, with_find = score_arm(tasks, with_rows)
    without_out, without_find = score_arm(tasks, without_rows)
    for finding in with_find:
        print(f"FAIL with: {finding}")
    for finding in without_find:
        print(f"FAIL without: {finding}")
    record = summarize(skill, tasks, with_out, without_out)
    golden = getattr(args, "golden", None)
    if golden:
        ok_golden, reason = check_trial_golden(record, Path(golden), getattr(args, "update_golden", False))
        if not ok_golden:
            print("FAIL golden: " + str(reason))
            print("RESULT FAIL")
            return 1
    out = Path(args.out) if args.out else ROOT / "skills" / skill / "references" / "trial-proof.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"runs {record['runs']}, with_rate {record['with_rate']}, "
          f"without_rate {record['without_rate']}, lift {record['lift']}, "
          f"spread {record['spread']}")
    print(f"proof {out}")
    print("RESULT PASS" if record["ok"] else "RESULT FAIL")
    return 0 if record["ok"] else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Skill trial runner: stranger sheet and with/wo grade.")
    sub = parser.add_subparsers(dest="command", required=True)
    sheet = sub.add_parser("sheet", help="print the task sheet a stranger runs cold")
    sheet.add_argument("--skill", required=True, help="skill name, e.g. pipe-run")
    sheet.add_argument("--evals", default=None, help="evals dir (default evals/)")
    sheet.set_defaults(func=cmd_sheet)
    grade = sub.add_parser("grade", help="score with/without arms and write trial-proof.json")
    grade.add_argument("--skill", required=True, help="skill name, e.g. pipe-run")
    grade.add_argument("--trials", default=None, help="trials dir (default work/trials/<name>/)")
    grade.add_argument("--evals", default=None, help="evals dir (default evals/)")
    grade.add_argument("--out", default=None, help="proof path (default skills/<name>/references/trial-proof.json)")
    grade.add_argument("--golden", default=None, help="golden file holding frozen runs/with_rate/lift (drift refuses without --update-golden)")
    grade.add_argument("--update-golden", action="store_true", help="rewrite the golden file instead of comparing (or set SKILL_TRIAL_UPDATE_GOLDEN=1)")
    grade.set_defaults(func=cmd_grade)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
