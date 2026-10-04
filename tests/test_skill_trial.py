"""TS-3 [TOOL] skill trial runner: sheet hides grading keys, grade gates runs/rate/lift."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

from tools import skill_trial as trial

ROOT = Path(__file__).resolve().parent.parent


def _write_sheet(evals: Path, skill: str, tasks: list[dict]) -> None:
    evals.mkdir(parents=True, exist_ok=True)
    (evals / f"{skill}_trials.jsonl").write_text(
        "\n".join(json.dumps(t) for t in tasks) + "\n", encoding="utf-8")


def _write_arms(trials: Path, with_rows: list[dict], without_rows: list[dict]) -> None:
    trials.mkdir(parents=True, exist_ok=True)
    (trials / "with.jsonl").write_text(
        "\n".join(json.dumps(r) for r in with_rows) + "\n", encoding="utf-8")
    (trials / "without.jsonl").write_text(
        "\n".join(json.dumps(r) for r in without_rows) + "\n", encoding="utf-8")


def _twelve(color: str = "ok") -> list[dict]:
    """A 12-task sheet: 6 run tasks (one refuses exit 2 on purpose) + 6 answer tasks."""
    tasks = []
    for n in range(1, 7):
        task: dict = {"id": f"r{n:02d}", "kind": "run",
                      "task": f"do run thing {n} {color}", "must": [f"did-{n}"]}
        if n == 6:
            task["exit"] = 2
            task["must"] = ["refused-6"]
        tasks.append(task)
    for n in range(7, 13):
        tasks.append({"id": f"a{n:02d}", "kind": "answer",
                      "task": f"say answer thing {n} {color}",
                      "must": [f"word-{n}"], "must_not": ["nope"]})
    return tasks


def _pass_row(task: dict) -> dict:
    row: dict = {"id": task["id"], "answer": " ".join(task.get("must", ["x"]))}
    if task["kind"] == "run":
        row["run"] = {"exit": task.get("exit", 0),
                      "output": " ".join(task.get("must", ["x"]))}
    return row


def _fail_row(task: dict) -> dict:
    return {"id": task["id"], "answer": "something else entirely"}


def test_sheet_prints_tasks_but_hides_grading_keys(tmp_path: Path, capsys) -> None:
    evals = tmp_path / "evals"
    _write_sheet(evals, "demo", _twelve())
    rc = trial.main(["sheet", "--skill", "demo", "--evals", str(evals)])
    out = capsys.readouterr().out
    assert rc == 0 and "RESULT PASS" in out
    assert "do run thing 1" in out and "tasks 12 (run 6, answer 6)" in out
    assert "did-1" not in out and "word-7" not in out  # grading keys stay hidden


def test_sheet_rejects_duplicate_ids(tmp_path: Path, capsys) -> None:
    evals = tmp_path / "evals"
    tasks = _twelve()
    tasks.append(dict(tasks[0]))
    _write_sheet(evals, "demo", tasks)
    assert trial.main(["sheet", "--skill", "demo", "--evals", str(evals)]) == 1
    assert "duplicate id" in capsys.readouterr().out


def test_grade_pass_writes_proof_with_all_keys(tmp_path: Path) -> None:
    evals, trials = tmp_path / "evals", tmp_path / "trials"
    tasks = _twelve()
    _write_sheet(evals, "demo", tasks)
    _write_arms(trials, [_pass_row(t) if t["id"] != "a12" else _fail_row(t) for t in tasks],
                [_pass_row(t) if t["id"] in ("a07", "a08", "r01", "r02", "r03") else _fail_row(t)
                 for t in tasks])
    out = tmp_path / "trial-proof.json"
    rc = trial.main(["grade", "--skill", "demo", "--evals", str(evals),
                     "--trials", str(trials), "--out", str(out)])
    assert rc == 0
    record = json.loads(out.read_text(encoding="utf-8"))
    assert record["runs"] == 12
    assert record["with_rate"] == pytest.approx(11 / 12, abs=1e-4)
    assert record["without_rate"] == pytest.approx(5 / 12, abs=1e-4)
    assert record["lift"] == pytest.approx(0.5, abs=1e-4)
    assert set(("runs", "with_rate", "without_rate", "lift", "spread", "fingerprint")) <= set(record)
    assert len(record["fingerprint"]) == 64


def test_grade_refuses_under_ten_runs(tmp_path: Path, capsys) -> None:
    evals, trials = tmp_path / "evals", tmp_path / "trials"
    tasks = _twelve()[:6]
    _write_sheet(evals, "demo", tasks)
    _write_arms(trials, [_pass_row(t) for t in tasks], [_fail_row(t) for t in tasks])
    out = tmp_path / "trial-proof.json"
    assert trial.main(["grade", "--skill", "demo", "--evals", str(evals),
                       "--trials", str(trials), "--out", str(out)]) == 1
    assert "RESULT FAIL" in capsys.readouterr().out


def test_grade_refuses_weak_with_rate_and_weak_lift(tmp_path: Path) -> None:
    evals, trials = tmp_path / "evals", tmp_path / "trials"
    tasks = _twelve()
    _write_sheet(evals, "demo", tasks)
    weak = [_pass_row(t) if int(t["id"][1:]) <= 9 else _fail_row(t) for t in tasks]
    _write_arms(trials, weak, [_fail_row(t) for t in tasks])
    out = tmp_path / "trial-proof.json"
    assert trial.main(["grade", "--skill", "demo", "--evals", str(evals),
                       "--trials", str(trials), "--out", str(out)]) == 1  # 9/12 = 0.75
    strong = [_pass_row(t) for t in tasks]
    _write_arms(trials, strong, [_pass_row(t) if int(t["id"][1:]) <= 10 else _fail_row(t)
                                for t in tasks])
    assert trial.main(["grade", "--skill", "demo", "--evals", str(evals),
                       "--trials", str(trials), "--out", str(out)]) == 1  # lift 2/12


def test_grade_refuses_run_answer_without_run_output(tmp_path: Path, capsys) -> None:
    evals, trials = tmp_path / "evals", tmp_path / "trials"
    tasks = _twelve()
    _write_sheet(evals, "demo", tasks)
    rows = [_pass_row(t) if int(t["id"][1:]) <= 9 else _fail_row(t) for t in tasks]
    rows[0] = {"id": "r01", "answer": "did-1 in words but never ran it"}
    _write_arms(trials, rows, [_fail_row(t) for t in tasks])
    out = tmp_path / "trial-proof.json"
    assert trial.main(["grade", "--skill", "demo", "--evals", str(evals),
                       "--trials", str(trials), "--out", str(out)]) == 1
    assert "refused: run task 'r01' has no run output" in capsys.readouterr().out


def test_command_line_sheet_and_grade(tmp_path: Path) -> None:
    evals, trials = tmp_path / "evals", tmp_path / "trials"
    tasks = _twelve()
    _write_sheet(evals, "demo", tasks)
    _write_arms(trials, [_pass_row(t) for t in tasks], [_fail_row(t) for t in tasks])
    out = tmp_path / "trial-proof.json"
    tool = str(ROOT / "tools" / "skill_trial.py")
    run = lambda *a: subprocess.run(  # noqa: E731
        [sys.executable, tool, *a], capture_output=True, text=True)
    assert run("sheet", "--skill", "demo", "--evals", str(evals)).returncode == 0
    good = run("grade", "--skill", "demo", "--evals", str(evals),
               "--trials", str(trials), "--out", str(out))
    assert good.returncode == 0 and "lift 1.0" in good.stdout
