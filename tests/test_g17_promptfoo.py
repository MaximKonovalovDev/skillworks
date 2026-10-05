"""G-17 promptfoo trial harness: 12 tasks before/after plus lift plus CI gate."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "g17-promptfoo.py"
YAML = ROOT / "evals" / "g17-trial.yaml"


def load_runner():
    spec = importlib.util.spec_from_file_location("g17_promptfoo", TOOL)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_yaml_holds_twelve_tasks() -> None:
    g17 = load_runner()
    _, cases, problems = g17.load_yaml(YAML)
    assert problems == []
    assert len(cases) == 12
    ids = [c["id"] for c in cases]
    assert len(set(ids)) == 12
    for case in cases:
        assert case["kind"] in ("run", "answer")
        assert case["task"].strip()
        assert isinstance(case["must"], list)


def test_every_case_has_before_and_after() -> None:
    g17 = load_runner()
    _, cases, _ = g17.load_yaml(YAML)
    for case in cases:
        assert case["before"].strip(), case["id"]
        assert case["after"].strip(), case["id"]


def test_lift_math() -> None:
    g17 = load_runner()
    _, cases, _ = g17.load_yaml(YAML)
    record = g17.grade(cases, {"min_runs": 12, "min_with_rate": 0.8, "min_lift": 0.3})
    assert record["runs"] == 12
    assert record["with_rate"] == pytest.approx(11 / 12, abs=1e-4)
    assert record["without_rate"] == pytest.approx(3 / 12, abs=1e-4)
    assert record["lift"] == pytest.approx(0.6667, abs=1e-4)
    assert record["lift_stderr"] == pytest.approx(0.1421, abs=1e-4)
    assert record["ok"] is True


def test_run_writes_proof_and_passes(tmp_path: Path, capsys) -> None:
    g17 = load_runner()
    out = tmp_path / "proof.json"
    assert g17.main(["run", "--yaml", str(YAML), "--out", str(out)]) == 0
    assert "RESULT PASS" in capsys.readouterr().out
    record = json.loads(out.read_text(encoding="utf-8"))
    for key in ("runs", "with_rate", "without_rate", "lift", "lift_stderr",
                "spread", "thresholds", "fingerprint", "ok"):
        assert key in record, key
    assert record["runs"] == 12 and record["ok"] is True
    assert len(record["fingerprint"]) == 64


def _write_yaml(path: Path, cases: list[dict]) -> None:
    lines = ["suite: g17-trial", "pattern: promptfoo", "thresholds:",
             "  min_runs: 12", "  min_with_rate: 0.8", "  min_lift: 0.3", "cases:"]
    for case in cases:
        must = "[" + ", ".join(case["must"]) + "]"
        lines += [f"  - id: {case['id']}", f"    kind: {case['kind']}",
                  f'    task: "{case["task"]}"', f"    must: {must}",
                  "    must_not: []", f'    before: "{case["before"]}"',
                  f'    after: "{case["after"]}"']
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_ci_fails_when_lift_misses_gate(tmp_path: Path, capsys) -> None:
    g17 = load_runner()
    _, cases, _ = g17.load_yaml(YAML)
    flat = [{"id": c["id"], "kind": c["kind"], "task": "task",
             "must": ["word"], "before": "word here", "after": "word here"}
            for c in cases]
    sheet = tmp_path / "flat.yaml"
    _write_yaml(sheet, flat)
    out = tmp_path / "proof.json"
    assert g17.main(["run", "--yaml", str(sheet), "--out", str(out)]) == 1
    assert "RESULT FAIL" in capsys.readouterr().out


def test_command_line_run(tmp_path: Path) -> None:
    out = tmp_path / "proof.json"
    run = subprocess.run(
        [sys.executable, str(TOOL), "run", "--yaml", str(YAML), "--out", str(out)],
        capture_output=True, text=True)
    assert run.returncode == 0
    assert "lift" in run.stdout and "RESULT PASS" in run.stdout


def test_command_line_sheet() -> None:
    run = subprocess.run(
        [sys.executable, str(TOOL), "sheet", "--yaml", str(YAML)],
        capture_output=True, text=True)
    assert run.returncode == 0 and "tasks 12" in run.stdout
