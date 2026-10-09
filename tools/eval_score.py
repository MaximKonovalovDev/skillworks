"""Eval upgrades: weighted partial credit plus failure score plus stderr (TS-6, R2).

Own original work (stdlib only, offline, no model calls, no network): no donor
code is copied. Shape ideas only from ai-evos/agent-skills
shared/eval_framework.py (Apache-2.0: skill-equipped versus bare-baseline runs
with the lift between them), stanfordnlp/dspy dspy/evaluate/evaluate.py (MIT:
per-example score plus a reasoning string carried beside it), and
EleutherAI/lm-evaluation-harness lm_eval/api/metrics.py (MIT: every aggregate
reported as mean plus the stderr of the mean).

What it does: binary pass/fail (book2skill/eval.py run_eval, tools/skill_trial.py
grade) cannot tell a near miss from a hard fail and prints lift with no error
bar. This module adds one shared metric, mean_stderr, used for all three error
bars, plus weighted partial credit per QA item:

    score 1.0  every must-word present (pass)
    score 0.5  some but not all must-words present (partial)
    score 0.0  no must-word present (hard fail)

Every scored item carries a reasoning field naming what was found or missed,
and the aggregate carries failure_score (the share of hard 0.0 fails) next to
the classic rate. The trial side reuses tools/skill_trial.py score_arm on the
same with/without arms and reports lift as the mean paired per-task difference
with its stderr from the same shared metric.

Command (offline)::

    python tools/eval_score.py report --skill <name> [--qa <file>] [--skill-dir <dir>]
        [--trials <dir>] [--evals <dir>] [--out <file>]

report grades evals/<skill>_qa.jsonl against the skill's own answer text with
the same top-5 rank the export gate uses, scores work/trials/<skill> arms when
present, writes one JSON report (default work/eval-score/<skill>-eval-score.json,
kept out of skills/ so fleet live-proof fingerprints never move) carrying rate,
weighted_rate, failure_score, lift and lift_stderr, prints the numbers and one
RESULT line, and exits 0 when the report is written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from book2skill import eval as eval_mod  # noqa: E402
from tools import skill_trial as trial_mod  # noqa: E402

FULL, PARTIAL, FAIL = 1.0, 0.5, 0.0


def score_item(must: list[str], blob: str) -> tuple[float, str]:
    """Score one QA item with partial credit. Returns (score, reasoning)."""
    words = [str(w) for w in (must or []) if str(w)]
    if not words:
        return FULL, "no must-words (vacuous pass)"
    lowered = (blob or "").lower()
    missing = [w for w in words if w.lower() not in lowered]
    found = len(words) - len(missing)
    if not missing:
        return FULL, f"all {len(words)} must-words present"
    if found == 0:
        return FAIL, f"no must-words present (hard fail, missed {len(words)}: {', '.join(words[:5])})"
    return PARTIAL, (
        f"partial {found}/{len(words)} must-words present; "
        f"missing: {', '.join(missing[:5])}"
    )


def mean_stderr(xs: list[float]) -> tuple[float, float]:
    """Shared metric: mean plus the stderr of the mean (sample std / sqrt(n)).

    n == 0 gives (0.0, 0.0); n == 1 gives (x, 0.0). Used for the weighted
    rate, the binary rate, and the paired lift differences alike.
    """
    n = len(xs)
    if n == 0:
        return 0.0, 0.0
    mean = sum(xs) / n
    if n == 1:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, math.sqrt(var / n)


# Steal (fresh port, MIT): seed-fixed 95 percent percentile bootstrap CI idea from
# michaelofengenden/agenttimebench (MIT, arXiv 2610.09944)
# https://github.com/michaelofengenden/agenttimebench/blob/main/duration_following/metrics.py
# (task_bootstrap there; geometric-mean deviation there). Rewritten here for lift
# paired diffs (arithmetic mean; geometric undefined for -1,0,1) stdlib only.
def task_bootstrap_ci(scores: list[float], seed: int = 0) -> tuple[float, float]:
    """Seed-fixed 95 percent percentile bootstrap CI for the mean."""
    n = len(scores)
    if n == 0:
        return 0.0, 0.0
    if n == 1:
        return float(scores[0]), float(scores[0])
    rng = random.Random(seed)
    n_boot = 2000
    means = []
    for _ in range(n_boot):
        s = sum(scores[rng.randrange(n)] for _ in range(n)) / n
        means.append(s)
    means.sort()
    lo = means[int(0.025 * n_boot)]
    hi = means[int(0.975 * n_boot) - 1]
    return lo, hi


# Steal (fresh port, Apache-2.0): Wilson 95 percent rate interval plus paired
# win/loss comparison idea from NVIDIA/SkillEvaluator@f32c884
# (arXiv 2608.20614), file src/skillevaluator/tier3/harbor/collector.py
# https://github.com/NVIDIA/SkillEvaluator/blob/f32c88455b6007b7afca9d1d3909283226d52efa/src/skillevaluator/tier3/harbor/collector.py
# licence Apache-2.0 (see LICENSE in that repo),
# paper https://arxiv.org/abs/2608.20614. Rewritten here stdlib only (math):
# Wilson score bounds replace the plus-minus 0.0 false-certainty at 12/12 or
# 0/N, and the paired comparison counts with-skill-only wins vs losses.
def _wilson_score_interval(passed: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95 percent score interval for a binomial rate (stdlib only)."""
    if total <= 0:
        return 0.0, 0.0
    p = max(0.0, min(1.0, float(passed) / float(total)))
    denom = 1.0 + z * z / total
    centre = p + z * z / (2.0 * total)
    delta = z * math.sqrt(p * (1.0 - p) / total + z * z / (4.0 * total * total))
    lo = max(0.0, (centre - delta) / denom)
    hi = min(1.0, (centre + delta) / denom)
    return lo, hi


def rate_interval(passed: int, total: int, z: float = 1.96) -> tuple[float, float]:
    """Public alias for the Wilson 95 percent rate interval."""
    return _wilson_score_interval(passed, total, z)


def _paired_pass_comparison(tasks: list[dict], with_rows: list[dict],
                            without_rows: list[dict]) -> dict:
    """Paired with-skill vs without-skill pass comparison (stdlib only)."""
    if not tasks:
        return {
            "paired_cases": 0,
            "with_skill_only_pass": 0,
            "without_skill_only_pass": 0,
            "both_pass": 0,
            "both_fail": 0,
            "pairing_status": "no-trials",
        }
    with_out, _ = trial_mod.score_arm(tasks, with_rows)
    without_out, _ = trial_mod.score_arm(tasks, without_rows)
    wins = losses = both_pass = both_fail = 0
    for t in tasks:
        w = bool(with_out[t["id"]])
        wo = bool(without_out[t["id"]])
        if w and not wo:
            wins += 1
        elif wo and not w:
            losses += 1
        elif w and wo:
            both_pass += 1
        else:
            both_fail += 1
    return {
        "paired_cases": len(tasks),
        "with_skill_only_pass": wins,
        "without_skill_only_pass": losses,
        "both_pass": both_pass,
        "both_fail": both_fail,
        "pairing_status": "paired",
    }


def grade_qa(items: list[dict], blobs: list[str]) -> dict:
    """Aggregate scored QA items into rate, weighted_rate and failure_score."""
    scored = []
    for item, blob in zip(items, blobs):
        score, reasoning = score_item(item.get("must", []), blob)
        scored.append({"q": item.get("q", ""), "score": score, "reasoning": reasoning})
    n = len(scored)
    scores = [s["score"] for s in scored]
    passes = [1.0 if s == FULL else 0.0 for s in scores]
    fails = [1.0 if s == FAIL else 0.0 for s in scores]
    rate, rate_stderr = mean_stderr(passes)
    weighted_rate, weighted_stderr = mean_stderr(scores)
    failure_score, _ = mean_stderr(fails)
    passed = int(sum(passes))
    wilson_lo, wilson_hi = _wilson_score_interval(passed, n)
    return {
        "n": n,
        "rate": round(rate, 4),
        "rate_stderr": round(rate_stderr, 4),
        "weighted_rate": round(weighted_rate, 4),
        "weighted_stderr": round(weighted_stderr, 4),
        "failure_score": round(failure_score, 4),
        "rate_ci_lo": round(wilson_lo, 4),
        "rate_ci_hi": round(wilson_hi, 4),
        "rate_interval": [round(wilson_lo, 4), round(wilson_hi, 4)],
        "items": scored,
    }


def _read_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def answer_blob(skill_dir: Path, query: str) -> str:
    """The skill's own answer blob for one question (same top-5 rank as the gate)."""
    texts = eval_mod.skill_answer_texts(skill_dir)
    if not texts:
        return ""
    return " ".join(text for _, text in eval_mod._rank(texts, query, limit=5))


def lift_with_stderr(tasks: list[dict], with_rows: list[dict],
                     without_rows: list[dict]) -> dict | None:
    """Lift from the same arms skill_trial grades, plus its stderr.

    Returns None when the sheet has no tasks. Paired difference per task:
    with_pass - without_pass in {-1, 0, 1}; lift is the mean, lift_stderr the
    shared-metric stderr of those differences.
    """
    if not tasks:
        return None
    with_out, _ = trial_mod.score_arm(tasks, with_rows)
    without_out, _ = trial_mod.score_arm(tasks, without_rows)
    diffs = [
        (1.0 if with_out[t["id"]] else 0.0) - (1.0 if without_out[t["id"]] else 0.0)
        for t in tasks
    ]
    lift, lift_stderr = mean_stderr(diffs)
    ci_lo, ci_hi = task_bootstrap_ci(diffs)
    runs = len(tasks)
    with_pass = int(sum(1.0 if with_out[t["id"]] else 0.0 for t in tasks))
    without_pass = int(sum(1.0 if without_out[t["id"]] else 0.0 for t in tasks))
    with_ci_lo, with_ci_hi = _wilson_score_interval(with_pass, runs)
    without_ci_lo, without_ci_hi = _wilson_score_interval(without_pass, runs)
    paired = _paired_pass_comparison(tasks, with_rows, without_rows)
    with_rate = round(sum(1.0 if with_out[t["id"]] else 0.0 for t in tasks) / runs, 4)
    without_rate = round(sum(1.0 if without_out[t["id"]] else 0.0 for t in tasks) / runs, 4)
    return {
        "runs": runs,
        "with_rate": with_rate,
        "without_rate": without_rate,
        "lift": round(lift, 4),
        "lift_stderr": round(lift_stderr, 4),
        "lift_ci_lo": round(ci_lo, 4),
        "lift_ci_hi": round(ci_hi, 4),
        "with_rate_ci_lo": round(with_ci_lo, 4),
        "with_rate_ci_hi": round(with_ci_hi, 4),
        "without_rate_ci_lo": round(without_ci_lo, 4),
        "without_rate_ci_hi": round(without_ci_hi, 4),
        "paired_cases": paired["paired_cases"],
        "with_skill_only_pass": paired["with_skill_only_pass"],
        "without_skill_only_pass": paired["without_skill_only_pass"],
        "both_pass": paired["both_pass"],
        "both_fail": paired["both_fail"],
        "pairing_status": paired["pairing_status"],
    }


def cmd_report(args: argparse.Namespace) -> int:
    skill = args.skill
    qa_path = Path(args.qa) if args.qa else ROOT / "evals" / f"{skill}_qa.jsonl"
    skill_dir = Path(args.skill_dir) if args.skill_dir else ROOT / "skills" / skill
    if not qa_path.is_file():
        print(f"FAIL no QA file {qa_path}")
        print("RESULT FAIL")
        return 1
    try:
        eval_mod.validate_qa(qa_path)
    except ValueError as exc:
        print(f"FAIL {exc}")
        print("RESULT FAIL")
        return 1
    items = _read_jsonl(qa_path)
    if not eval_mod.skill_answer_texts(skill_dir):
        print(f"FAIL no answer text in {skill_dir}")
        print("RESULT FAIL")
        return 1
    qa = grade_qa(items, [answer_blob(skill_dir, i.get("q", "")) for i in items])

    trials: dict | None = None
    trials_note = "no trials"
    evals_dir = Path(args.evals) if args.evals else ROOT / "evals"
    sheet_path = evals_dir / f"{skill}_trials.jsonl"
    trials_dir = Path(args.trials) if args.trials else ROOT / "work" / "trials" / skill
    if sheet_path.is_file():
        tasks, problems = trial_mod.load_sheet(skill, evals_dir)
        with_path, without_path = trials_dir / "with.jsonl", trials_dir / "without.jsonl"
        if problems:
            trials_note = f"no trials: sheet has {len(problems)} problems"
        elif not with_path.is_file() or not without_path.is_file():
            trials_note = f"no trials: arms missing in {trials_dir}"
        else:
            trials = lift_with_stderr(tasks, _read_jsonl(with_path),
                                      _read_jsonl(without_path))
            trials_note = f"trials {trials['runs']} runs" if trials else "no trials"

    canonical = json.dumps(
        {"qa": [(s["q"], s["score"]) for s in qa["items"]],
         "trials": trials},
        sort_keys=True, ensure_ascii=True)
    record = {
        "skill": skill,
        "n_qa": qa["n"],
        "rate": qa["rate"],
        "rate_stderr": qa["rate_stderr"],
        "weighted_rate": qa["weighted_rate"],
        "weighted_stderr": qa["weighted_stderr"],
        "failure_score": qa["failure_score"],
        "runs": trials["runs"] if trials else 0,
        "with_rate": trials["with_rate"] if trials else None,
        "without_rate": trials["without_rate"] if trials else None,
        "lift": trials["lift"] if trials else None,
        "lift_stderr": trials["lift_stderr"] if trials else None,
        "lift_ci_lo": trials["lift_ci_lo"] if trials else None,
        "lift_ci_hi": trials["lift_ci_hi"] if trials else None,
        "rate_ci_lo": qa["rate_ci_lo"],
        "rate_ci_hi": qa["rate_ci_hi"],
        "rate_interval": qa["rate_interval"],
        "with_rate_ci_lo": trials["with_rate_ci_lo"] if trials else None,
        "with_rate_ci_hi": trials["with_rate_ci_hi"] if trials else None,
        "without_rate_ci_lo": trials["without_rate_ci_lo"] if trials else None,
        "without_rate_ci_hi": trials["without_rate_ci_hi"] if trials else None,
        "paired_cases": trials["paired_cases"] if trials else 0,
        "with_skill_only_pass": trials["with_skill_only_pass"] if trials else 0,
        "without_skill_only_pass": trials["without_skill_only_pass"] if trials else 0,
        "pairing_status": trials["pairing_status"] if trials else "no-trials",
        "trials_note": trials_note,
        "fingerprint": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
    }
    out = Path(args.out) if args.out else ROOT / "work" / "eval-score" / f"{skill}-eval-score.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(f"qa {qa['n']}: rate {qa['rate']} +/- {qa['rate_stderr']}, "
          f"weighted_rate {qa['weighted_rate']} +/- {qa['weighted_stderr']}, "
          f"failure_score {qa['failure_score']}")
    if trials:
        print(f"trials {trials['runs']}: with {trials['with_rate']} "
              f"without {trials['without_rate']}, lift {trials['lift']} "
              f"+/- {trials['lift_stderr']}")
    else:
        print(trials_note)
    print(f"proof {out}")
    min_rate = getattr(args, "min_rate", None)
    if min_rate is not None and qa["rate"] < min_rate:
        print(f"FAIL rate {qa['rate']} below --min-rate {min_rate}")
        print("RESULT FAIL")
        return 1
    print("RESULT PASS")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Eval upgrades: partial credit, failure score, stderr.")
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("report", help="write one skill report with rate, weighted_rate and lift stderr")
    rep.add_argument("--skill", required=True, help="skill name, e.g. pipe-run")
    rep.add_argument("--qa", default=None, help="QA file (default evals/<skill>_qa.jsonl)")
    rep.add_argument("--skill-dir", default=None, help="skill dir (default skills/<skill>)")
    rep.add_argument("--trials", default=None, help="trials dir (default work/trials/<skill>/)")
    rep.add_argument("--evals", default=None, help="evals dir (default evals/)")
    rep.add_argument("--out", default=None, help="report path (default work/eval-score/<skill>-eval-score.json)")
    rep.add_argument("--min-rate", type=float, default=None,
                     help="fail when QA rate is below this (e.g. 0.6 export gate)")
    rep.set_defaults(func=cmd_report)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
