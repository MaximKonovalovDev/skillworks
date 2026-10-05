"""TS-6 [TOOL] eval upgrades: weighted partial credit, failure score, stderr."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import eval_score as es

ROOT = Path(__file__).resolve().parent.parent


def test_score_item_full_partial_fail_and_reasoning() -> None:
    score, why = es.score_item(["alpha", "beta"], "Alpha and beta here")
    assert score == 1.0 and "all 2" in why
    score, why = es.score_item(["alpha", "beta"], "only alpha here")
    assert score == 0.5 and "beta" in why  # reasoning names the miss
    score, why = es.score_item(["alpha", "beta"], "nothing relevant")
    assert score == 0.0 and "hard fail" in why
    score, _ = es.score_item([], "anything")
    assert score == 1.0  # vacuous pass, matches the gate's all([]) == True


def test_score_item_case_insensitive() -> None:
    assert es.score_item(["DRY-RUN"], "dry-run output")[0] == 1.0


def test_mean_stderr_shared_metric() -> None:
    assert es.mean_stderr([]) == (0.0, 0.0)
    assert es.mean_stderr([2.0]) == (2.0, 0.0)
    mean, se = es.mean_stderr([1.0, 1.0, 1.0, 1.0])
    assert mean == pytest.approx(1.0) and se == pytest.approx(0.0)
    mean, se = es.mean_stderr([1.0, 0.0])
    assert mean == pytest.approx(0.5) and se == pytest.approx(0.5)


def test_grade_qa_rates_and_failure_score() -> None:
    items = [{"q": "q1", "must": ["a"]}, {"q": "q2", "must": ["a", "b"]},
             {"q": "q3", "must": ["zzz"]}]
    blobs = ["a present", "a present", "nothing"]
    qa = es.grade_qa(items, blobs)
    assert qa["n"] == 3
    assert qa["rate"] == pytest.approx(1 / 3, abs=1e-4)
    assert qa["weighted_rate"] == pytest.approx((1.0 + 0.5 + 0.0) / 3, abs=1e-4)
    assert qa["failure_score"] == pytest.approx(1 / 3, abs=1e-4)
    assert all(set(("q", "score", "reasoning")) <= set(s) for s in qa["items"])


def _write(path: Path, rows: list[dict]) -> None:
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_lift_with_stderr_paired_diffs() -> None:
    tasks = [{"id": "t1", "kind": "answer", "task": "t", "must": ["w1"]},
             {"id": "t2", "kind": "answer", "task": "t", "must": ["w2"]},
             {"id": "t3", "kind": "answer", "task": "t", "must": ["w3"]},
             {"id": "t4", "kind": "answer", "task": "t", "must": ["w4"]}]
    with_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "w2"},
                 {"id": "t3", "answer": "w3"}, {"id": "t4", "answer": "nope"}]
    without_rows = [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "nope"},
                    {"id": "t3", "answer": "nope"}, {"id": "t4", "answer": "nope"}]
    got = es.lift_with_stderr(tasks, with_rows, without_rows)
    assert got is not None
    assert got["runs"] == 4 and got["lift"] == pytest.approx(0.5, abs=1e-4)
    # paired diffs [0, 1, 1, 0]: mean 0.5, sample stderr sqrt(1/3 / 4)
    assert got["lift_stderr"] == pytest.approx(0.2887, abs=1e-4)
    assert es.lift_with_stderr([], [], []) is None


def test_report_writes_one_skill_report_with_all_keys(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when demoing the report.\n---\n\n"
        "The dry run prints DRY-RUN and spends tokens.\n", encoding="utf-8")
    evals = tmp_path / "evals"
    evals.mkdir()
    _write(evals / "demo_qa.jsonl", [
        {"q": "dry run prints", "must": ["DRY-RUN"]},
        {"q": "dry run tokens", "must": ["tokens", "bananas"]},
        {"q": "xylophone trumpet", "must": ["xylophone"]},
    ])
    _write(evals / "demo_trials.jsonl", [
        {"id": "t1", "kind": "answer", "task": "say w1", "must": ["w1"]},
        {"id": "t2", "kind": "answer", "task": "say w2", "must": ["w2"]},
    ])
    trials = tmp_path / "trials"
    trials.mkdir()
    _write(trials / "with.jsonl", [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "w2"}])
    _write(trials / "without.jsonl", [{"id": "t1", "answer": "w1"}, {"id": "t2", "answer": "nope"}])
    out = tmp_path / "report.json"
    rc = es.main(["report", "--skill", "demo", "--skill-dir", str(skill_dir),
                  "--qa", str(evals / "demo_qa.jsonl"), "--evals", str(evals),
                  "--trials", str(trials), "--out", str(out)])
    assert rc == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    for key in ("rate", "weighted_rate", "failure_score", "lift", "lift_stderr",
                "rate_stderr", "weighted_stderr", "fingerprint"):
        assert key in record, key
    assert record["n_qa"] == 3 and record["runs"] == 2
    assert record["rate"] == pytest.approx(1 / 3, abs=1e-4)
    assert record["weighted_rate"] == pytest.approx(0.5, abs=1e-4)
    assert record["lift"] == pytest.approx(0.5, abs=1e-4)
    assert len(record["fingerprint"]) == 64


def test_report_without_trials_still_passes(tmp_path: Path, capsys) -> None:
    skill_dir = tmp_path / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when demoing the report.\n---\n\nwords here.\n",
        encoding="utf-8")
    evals = tmp_path / "evals"
    evals.mkdir()
    _write(evals / "demo_qa.jsonl", [{"q": "what words?", "must": ["words"]}])
    out = tmp_path / "report.json"
    assert es.main(["report", "--skill", "demo", "--skill-dir", str(skill_dir),
                    "--qa", str(evals / "demo_qa.jsonl"), "--evals", str(evals),
                    "--trials", str(tmp_path / "missing"), "--out", str(out)]) == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["lift"] is None and record["lift_stderr"] is None
    assert "no trials" in capsys.readouterr().out


def test_report_refuses_missing_qa(tmp_path: Path, capsys) -> None:
    out = tmp_path / "report.json"
    assert es.main(["report", "--skill", "demo", "--qa", str(tmp_path / "no.jsonl"),
                    "--out", str(out)]) == 1
    assert "RESULT FAIL" in capsys.readouterr().out


def test_command_line_report(tmp_path: Path) -> None:
    skill_dir = tmp_path / "skills" / "demo"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\nname: demo\ndescription: Use when demoing the report.\n---\n\nwords here.\n",
        encoding="utf-8")
    evals = tmp_path / "evals"
    evals.mkdir()
    _write(evals / "demo_qa.jsonl", [{"q": "what words?", "must": ["words"]}])
    out = tmp_path / "report.json"
    tool = str(ROOT / "tools" / "eval_score.py")
    run = subprocess.run(
        [sys.executable, tool, "report", "--skill", "demo",
         "--skill-dir", str(skill_dir), "--qa", str(evals / "demo_qa.jsonl"),
         "--evals", str(evals), "--out", str(out)],
        capture_output=True, text=True)
    assert run.returncode == 0 and "weighted_rate" in run.stdout
