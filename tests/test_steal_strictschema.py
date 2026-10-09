"""STEAL PORT strict unknown-field refuse plus collect-all QA errors (lap 5, wave 4)."""
import json
from pathlib import Path

from book2skill.eval import (
    UNKNOWN_FIELD,
    ErrorDefinition,
    ErrorList,
    Schema,
    Use,
    validate_qa,
    validate_qa_all,
    validate_receipt,
    validate_trial_proof,
)


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


def test_unknown_receipt_flagged():
    record = dict(_good_receipt(), extra="oops")
    errors = validate_receipt(record)
    assert errors
    assert any(UNKNOWN_FIELD.code in e and "extra" in e for e in errors)


def test_unknown_proof_flagged():
    bad = dict(_good_proof(), typo=1)
    errors = validate_trial_proof(bad)
    assert errors
    assert any(UNKNOWN_FIELD.code in e and "typo" in e for e in errors)


def test_schema_strict_and_purge():
    s = Schema({"a": Use(lambda v: v == 1)}, allow_unknown=False)
    assert s.allow_unknown is False
    errs = s.validate({"a": 1, "b": 2}, "f.json")
    assert any(UNKNOWN_FIELD.code in e for e in errs)
    s2 = Schema({"a": Use(lambda v: v == 1)}, allow_unknown=False, purge_unknown=True)
    rec = {"a": 1, "b": 2}
    assert s2.validate(rec, "f.json") == []
    assert rec == {"a": 1}
    s3 = Schema({"a": Use(lambda v: v == 1)}, allow_unknown=True)
    assert s3.validate({"a": 1, "b": 2}, "f.json") == []


def test_error_definition_and_list():
    assert isinstance(UNKNOWN_FIELD, ErrorDefinition)
    assert UNKNOWN_FIELD.code == "UNKNOWN_FIELD"
    assert isinstance(ErrorList(), list)


def test_qa_collect_all(tmp_path: Path):
    qa = tmp_path / "qa.jsonl"
    qa.write_text(
        "{\"q\": \"good?\", \"must\": [\"good\"]}\n"
        "not json\n"
        "{\"q\": \"bad?\", \"must\": \"oops\"}\n"
        "{\"q\": \"typo?\", \"must\": [\"x\"], \"mustt\": [\"x\"]}\n",
        encoding="utf-8",
    )
    errors = validate_qa_all(qa)
    assert isinstance(errors, ErrorList)
    assert len(errors) >= 3
    assert any("line 2" in e for e in errors)
    assert any("line 3" in e for e in errors)
    assert any("line 4" in e and UNKNOWN_FIELD.code in e for e in errors)
    try:
        validate_qa(qa)
        raised = False
    except ValueError as exc:
        raised = True
        assert "must" in str(exc) or UNKNOWN_FIELD.code in str(exc) or "JSON" in str(exc)
    assert raised


def test_qa_typo_refused(tmp_path: Path):
    qa = tmp_path / "qa.jsonl"
    qa.write_text(json.dumps({"q": "hi?", "must": ["hi"], "extra": 1}) + "\n", encoding="utf-8")
    errors = validate_qa_all(qa)
    assert len(errors) == 1
    assert UNKNOWN_FIELD.code in errors[0]
