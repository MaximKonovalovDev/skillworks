"""Steal bootstrap CI beside lift: seed-fixed 95 percent CI."""
from tools import eval_score as es


def test_same_seed_identical_ci():
    scores = [1.0, 0.0, 1.0, 0.0, 1.0, 0.5, 0.0, 1.0]
    lo1, hi1 = es.task_bootstrap_ci(scores, seed=7)
    lo2, hi2 = es.task_bootstrap_ci(scores, seed=7)
    assert (lo1, hi1) == (lo2, hi2)
    assert lo1 <= hi1


def test_ci_contains_mean():
    scores = [1.0, 0.0, 1.0, 1.0, 0.0, 0.5]
    lo, hi = es.task_bootstrap_ci(scores, seed=0)
    mean, _ = es.mean_stderr(scores)
    assert lo <= mean <= hi
    width = hi - lo
    assert width >= 0.0
    print(lo, hi, width, mean)


def test_lift_reports_ci_beside_lift():
    tasks = [{"id": "t1", "kind": "answer", "task": "t", "must": ["w1"]}, {"id": "t2", "kind": "answer", "task": "t", "must": ["w2"]}, {"id": "t3", "kind": "answer", "task": "t", "must": ["w3"]}, {"id": "t4", "kind": "answer", "task": "t", "must": ["w4"]}]
    with_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "w2"}, {"id": "t3", "answer": "w3"}, {"id": "t4", "answer": "nope"}]
    without_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "nope"}, {"id": "t3", "answer": "nope"}, {"id": "t4", "answer": "nope"}]
    got = es.lift_with_stderr(tasks, with_rows, without_rows)
    assert got is not None
    assert got["lift_ci_lo"] <= got["lift"] <= got["lift_ci_hi"]
    width = got["lift_ci_hi"] - got["lift_ci_lo"]
    assert width >= 0.0
    print(got["lift"], got["lift_ci_lo"], got["lift_ci_hi"], width)


def test_empty_and_single():
    assert es.task_bootstrap_ci([], seed=0) == (0.0, 0.0)
    assert es.task_bootstrap_ci([0.5], seed=0) == (0.5, 0.5)
