"""STEAL PORT pass@1/pass@k/pass^k repeat consistency + integer gate (gate-flip fix)."""
from tools import eval_score as es


def test_unstable_two_of_three_gate_pass_but_strict_fail() -> None:
    got = es.consistency([[1, 1, 0]], k=3, required=2)
    assert got["tasks"] == 1 and got["status"] == "ok"
    assert got["pass@1"] == 0.6667  # 2/3 single-repeat rate
    assert got["pass@k"] == 1.0  # any-pass hits
    assert got["pass^k"] == 0.0  # strict all-pass misses
    assert got["gate_pass"] == 1  # integer gate 2>=2 PASSES
    assert got["gate_rate"] == 1.0
    assert got["gate_flip"] == 1  # gate-flip cases detected: 1 (0->1)


def test_stable_and_empty_rollup() -> None:
    stable = es.consistency([[1, 1, 1]], k=3, required=2)
    assert stable["pass^k"] == 1.0 and stable["gate_flip"] == 0
    empty = es.consistency([], k=3, required=2)
    assert empty["tasks"] == 0 and empty["status"] == "N/A"
    assert empty["pass@1"] == 0.0 and empty["pass^k"] == 0.0

