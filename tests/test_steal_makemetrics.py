"""Steal check: make receipts carry per-stage timings (measure port)."""
import json

from book2skill.make import make


QA_GOOD = "{\"q\": \"how do I chain commands?\", \"must\": [\"semicolon\"]}\n{\"q\": \"what does a pipeline pass?\", \"must\": [\"objects\"]}\n"

QA_BAD = "{\"q\": \"what about zzzznothere?\", \"must\": [\"zzzznothere\"]}\n{\"q\": \"what about qqqqmissing?\", \"must\": [\"qqqqmissing\"]}\n"


def _manual(root):
    docs = root / "manual"
    (docs / "sub").mkdir(parents=True)
    (docs / "chain.md").write_text("Use a semicolon to chain commands in Windows PowerShell 5.1.", encoding="utf-8")
    (docs / "sub" / "pipe.md").write_text("A pipeline passes objects, not text.", encoding="utf-8")
    return docs


def test_make_receipt_has_six_stage_timings_and_total(tmp_path):
    docs = _manual(tmp_path)
    qa = tmp_path / "qa.jsonl"
    qa.write_text(QA_GOOD, encoding="utf-8")
    work = tmp_path / "work" / "demo"
    skill = tmp_path / "skills" / "demo"
    result = make(str(docs), "demo", "Use when chaining.", qa, work=work, skill=skill, say=lambda *a, **k: None)
    timings = result["timings"]
    assert set(timings) == {"extract", "split", "index", "build", "eval", "audit"}
    for stage in ("extract", "split", "index", "build", "eval", "audit"):
        assert isinstance(timings[stage], float)
        assert timings[stage] >= 0.0
    assert isinstance(result["total_s"], float)
    assert result["total_s"] >= 0.0
    assert result["total_s"] + 0.05 >= sum(timings.values())
    on_disk = json.loads((work / "make.json").read_text(encoding="utf-8"))
    assert on_disk["timings"] == timings
    assert on_disk["total_s"] == result["total_s"]
    print("makemetrics timings=%s total=%.3f" % (sorted(timings), result["total_s"]))


def test_make_refused_gate_still_records_timings(tmp_path):
    docs = _manual(tmp_path)
    qa = tmp_path / "qa.jsonl"
    qa.write_text(QA_BAD, encoding="utf-8")
    work = tmp_path / "work" / "demo"
    skill = tmp_path / "skills" / "demo"
    try:
        make(str(docs), "demo", "Use when chaining.", qa, work=work, skill=skill, say=lambda *a, **k: None)
        raise AssertionError("expected SystemExit")
    except SystemExit as exc:
        assert "eval gate refused" in str(exc)
    on_disk = json.loads((work / "make.json").read_text(encoding="utf-8"))
    assert set(on_disk["timings"]) == {"extract", "split", "index", "build", "eval", "audit"}
    assert on_disk["total_s"] >= 0.0
