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
    return {
        "n": n,
        "rate": round(rate, 4),
        "rate_stderr": round(rate_stderr, 4),
        "weighted_rate": round(weighted_rate, 4),
        "weighted_stderr": round(weighted_stderr, 4),
        "failure_score": round(failure_score, 4),
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
    runs = len(tasks)
    with_rate = round(sum(1.0 if with_out[t["id"]] else 0.0 for t in tasks) / runs, 4)
    without_rate = round(sum(1.0 if without_out[t["id"]] else 0.0 for t in tasks) / runs, 4)
    return {
        "runs": runs,
        "with_rate": with_rate,
        "without_rate": without_rate,
        "lift": round(lift, 4),
        "lift_stderr": round(lift_stderr, 4),
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
    rep.set_defaults(func=cmd_report)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
