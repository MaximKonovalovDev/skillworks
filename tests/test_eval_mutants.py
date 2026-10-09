# idea: egnaro9/evalmut (MIT) https://github.com/egnaro9/evalmut — mutate QA answers, grader must fail mutants.
"""Grader-mutation false-pass battery: mutate answers, not code diffs.

Distinct from diff-gate rows: replays the substring grader over corrupted
answers (blank / truncated / negated) and measures the false-pass rate.
Sanity: blank and garbage must FAIL. Negation keeps keywords so substring
grading still passes it — that known weakness is what the rate reports.
"""
from __future__ import annotations

FIXTURE = [
    {"q": "which gateway lanes exist",
     "must": ["chat", "vision"],
     "gold": "The gateway has chat and vision lanes."},
    {"q": "what happens without a provider key",
     "must": ["refuses", "key"],
     "gold": "It refuses the call without a key."},
    {"q": "how is batch work claimed",
     "must": ["lease", "requeue"],
     "gold": "Workers take a lease and requeue on expiry."},
]


def _grade(answer: str, must: list) -> bool:
    text = (answer or "").lower()
    return all(m.lower() in text for m in must)


def _qa_mutants(items: list) -> list:
    mutants = []
    for it in items:
        gold, must = it["gold"], it["must"]
        mutants.append((it["q"], "blank_output", ""))
        cut = gold.lower().find(must[0].lower())
        mutants.append((it["q"], "truncate_before_answer",
                        gold[:cut] if cut > 0 else ""))
        mutants.append((it["q"], "negation",
                        "It is false that " + gold
                        + " No " + ", ".join(must) + "."))
    return mutants


def false_pass_rate(mutants: list, by_q: dict) -> float:
    if not mutants:
        return 0.0
    passed = sum(1 for q, _op, ans in mutants if _grade(ans, by_q[q]))
    return passed / len(mutants)


def test_sanity_blank_and_garbage_fail() -> None:
    for it in FIXTURE:
        assert not _grade("", it["must"])
        assert not _grade("lorem ipsum dolor xyzzy", it["must"])
        assert _grade(it["gold"], it["must"])


def test_false_pass_rate_reported(capsys) -> None:
    by_q = {it["q"]: it["must"] for it in FIXTURE}
    mutants = _qa_mutants(FIXTURE)
    assert len(mutants) == 9
    rate = false_pass_rate(mutants, by_q)
    print(f"false-pass rate: {int(rate * len(mutants))}/{len(mutants)} ({rate:.2f})")
    blanks = [m for m in mutants if m[1] == "blank_output"]
    assert false_pass_rate(blanks, by_q) == 0.0
    assert rate == 3 / 9
