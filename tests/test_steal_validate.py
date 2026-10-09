"""Steal validate: keleshev/schema-style record checks warn, never fail writes."""
import json
import warnings
from pathlib import Path

from book2skill.eval import run_eval, validate_receipt, validate_trial_proof


def _good_receipt():
    return {"skill": "demo", "total": 2, "passed": 1, "rate": 0.5, "graded_on": "skill"}


def _good_proof():
    return {
        "runs": 10,
        "with_rate": 0.8,
        "without_rate": 0.5,
        "lift": 0.3,
        "spread": 0.3,
        "fingerprint": "ab" * 32,
    }


def test_good_receipt_passes():
    assert validate_receipt(_good_receipt()) == []
    assert validate_trial_proof(_good_proof()) == []


def test_missing_counts_flagged():
    record = {"skill": "demo", "passed": 1, "rate": 1.0, "graded_on": "skill"}
    errors = validate_receipt(record)
    assert errors
    assert any("total" in e or "counts" in e for e in errors)
    assert all(":" in e and e.startswith("eval_report.json:") for e in errors)


def test_bad_trial_proof_runs_flagged(tmp_path: Path):
    bad = dict(_good_proof(), runs="ten")
    errors = validate_trial_proof(bad)
    assert errors
    assert any("runs" in e for e in errors)
    assert all(e.startswith("trial-proof.json:") and ":" in e for e in errors)
    work = tmp_path / "work"
    (work / "chunks").mkdir(parents=True)
    (work / "chunks" / "0000.txt").write_text("hello world chapter about leases", encoding="utf-8")
    skill = tmp_path / "skill"
    (skill / "references").mkdir(parents=True)
    (skill / "references" / "trial-proof.json").write_text(json.dumps(bad), encoding="utf-8")
    (skill / "SKILL.md").write_text("---\nname: demo\ndescription: demo\n---\nAbout leases.\n", encoding="utf-8")
    qa = tmp_path / "qa.jsonl"
    qa.write_text("{\"q\": \"what about leases?\", \"must\": [\"leases\"]}\n", encoding="utf-8")
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        report = run_eval(work, skill, qa)
    assert (skill / "eval_report.json").exists()
    assert report["total"] == 1
    assert any("runs" in str(w.message) for w in caught)
