"""STEAL PORT Wilson 95 percent rate interval plus paired lift comparison (lap 5, wave 2)."""
import pytest

from tools import eval_score as es


def test_wilson_12_of_12_has_nonzero_width() -> None:
    lo, hi = es._wilson_score_interval(12, 12)
    assert hi == pytest.approx(1.0, abs=1e-4)
    assert lo < 1.0
    assert (hi - lo) > 0.0


def test_wilson_0_of_n_has_nonzero_width() -> None:
    lo, hi = es._wilson_score_interval(0, 12)
    assert lo == pytest.approx(0.0, abs=1e-9)
    assert hi > 0.0
    assert (hi - lo) > 0.0


def test_wilson_empty_is_zero() -> None:
    assert es._wilson_score_interval(0, 0) == (0.0, 0.0)


def test_grade_qa_carries_wilson_interval() -> None:
    items = [{"q": f"q{i}", "must": ["a"]} for i in range(12)]
    blobs = ["a present"] * 12
    qa = es.grade_qa(items, blobs)
    assert qa["rate"] == pytest.approx(1.0)
    assert qa["rate_stderr"] == pytest.approx(0.0)
    assert qa["rate_ci_lo"] < qa["rate_ci_hi"]
    assert qa["rate_ci_hi"] == pytest.approx(1.0, abs=1e-4)
    assert qa["rate_interval"][0] == pytest.approx(qa["rate_ci_lo"])
    assert qa["rate_interval"][1] == pytest.approx(qa["rate_ci_hi"])


def test_paired_counts_correct() -> None:
    tasks = [{"id": "t1", "kind": "answer", "task": "t", "must": ["w1"]},
             {"id": "t2", "kind": "answer", "task": "t", "must": ["w2"]},
             {"id": "t3", "kind": "answer", "task": "t", "must": ["w3"]},
             {"id": "t4", "kind": "answer", "task": "t", "must": ["w4"]}]
    with_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "w2"},
                 {"id": "t3", "answer": "w3"}, {"id": "t4", "answer": "nope"}]
    without_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "nope"},
                    {"id": "t3", "answer": "nope"}, {"id": "t4", "answer": "w4"}]
    got = es._paired_pass_comparison(tasks, with_rows, without_rows)
    assert got["paired_cases"] == 4
    assert got["with_skill_only_pass"] == 2
    assert got["without_skill_only_pass"] == 1
    assert got["pairing_status"] == "paired"


def test_lift_carries_paired_and_wilson() -> None:
    tasks = [{"id": "t1", "kind": "answer", "task": "t", "must": ["w1"]},
             {"id": "t2", "kind": "answer", "task": "t", "must": ["w2"]}]
    with_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "w2"}]
    without_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "nope"}]
    got = es.lift_with_stderr(tasks, with_rows, without_rows)
    assert got is not None
    assert got["paired_cases"] == 2
    assert got["with_skill_only_pass"] == 1
    assert got["pairing_status"] == "paired"
    assert got["with_rate_ci_lo"] < got["with_rate_ci_hi"]

