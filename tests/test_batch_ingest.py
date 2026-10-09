"""Batch ingest: manifest per doc plus merged chunks plus QA reports plus receipts.

Covers the batch tool (book2skill/batch.py): manifest.jsonl rows, merged
chunks, merged plus per-doc QA reports, merged plus per-doc receipts, the
sentence-window chunk option, and the k5 retrieve-QA honest fallback.
"""
import ast
import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from book2skill import batch as batch_mod
from book2skill import index as index_mod
from book2skill import split as split_mod
from book2skill.cli import main


def _two_docs(root: Path) -> Path:
    src = root / "docs"
    src.mkdir(parents=True)
    (src / "alpha.md").write_text(
        "# Alpha\n\nLeases guard batch queues. Requeue follows stuck leases quickly. "
        "The batch window keeps five sentences together for recall.\n",
        encoding="utf-8",
    )
    (src / "beta.md").write_text(
        "# Beta\n\nPipelines pass objects, not text. A semicolon chains commands in PowerShell. "
        "The operator question stays in its own doc.\n",
        encoding="utf-8",
    )
    return src


def _qa(root: Path) -> Path:
    qa = root / "qa.jsonl"
    qa.write_text(
        '{"q": "what guards batch queues?", "must": ["leases"]}\n'
        '{"q": "what does a pipeline pass?", "must": ["objects"]}\n'
        '{"q": "what about zzzznothere?", "must": ["zzzznothere"]}\n',
        encoding="utf-8",
    )
    return qa


def test_manifest_lists_one_row_per_doc_with_chunk_files(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    work = tmp_path / "work"
    receipt = batch_mod.ingest(str(src), work)
    assert receipt["docs"] == 2 and receipt["chunks"] >= 2
    rows = batch_mod.read_manifest(work)
    assert len(rows) == 2
    assert sorted(r["doc"] for r in rows) == ["alpha.md", "beta.md"]
    for row in rows:
        assert row["chars"] > 0 and row["chunks"] >= 1
        assert row["chunk_files"] and row["mode"] == "chars"
        for name in row["chunk_files"]:
            assert (work / "chunks" / name).is_file()
    # merged chunks carry the doc header so hits stay attributable
    texts = [(work / "chunks" / n).read_text(encoding="utf-8") for n in sorted((work / "chunks").glob("*.txt"))]
    assert any("# doc: alpha.md" in t for t in texts)
    assert any("# doc: beta.md" in t for t in texts)
    assert (work / "index.jsonl").is_file()
    assert (work / "manifest.jsonl").is_file()


def test_receipts_merged_plus_per_doc(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    work = tmp_path / "work"
    receipt = batch_mod.ingest(str(src), work)
    assert receipt["stage"] == "batch"
    assert (work / "batch.json").is_file()
    assert (work / "receipt.json").is_file()
    assert json.loads((work / "batch.json").read_text(encoding="utf-8")) == receipt
    per = sorted((work / "receipts").glob("*.json"))
    assert len(per) == 2
    for p in per:
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["stage"] == "batch-doc" and data["chunks"] >= 1 and data["chunk_files"]


def test_sentence_window_option_chunks_by_sentences(tmp_path: Path) -> None:
    text = "One goes first. Two follows it. Three keeps going. Four still runs. Five ends well. Six starts again."
    chunks = split_mod.chunk_text(text, mode="sentences", window=2, sent_overlap=1)
    assert chunks == [
        "One goes first. Two follows it.",
        "Two follows it. Three keeps going.",
        "Three keeps going. Four still runs.",
        "Four still runs. Five ends well.",
        "Five ends well. Six starts again.",
    ]
    # the work-level split keeps the same helper, one home per concern
    work = tmp_path / "work"
    work.mkdir()
    (work / "full_text.txt").write_text(text, encoding="utf-8")
    receipt = split_mod.split(work, mode="sentences", window=2, sent_overlap=1)
    assert receipt["mode"] == "sentences" and receipt["window"] == 2 and receipt["chunks"] == 5
    # batch exposes the same option end to end
    src = _two_docs(tmp_path)
    work2 = tmp_path / "work2"
    receipt2 = batch_mod.ingest(str(src), work2, chunk_mode="sentences", window=2, sent_overlap=1)
    assert receipt2["chunk_mode"] == "sentences" and receipt2["window"] == 2
    assert batch_mod.read_manifest(work2)[0]["mode"] == "sentences"


def test_chars_mode_stays_backward_compatible(tmp_path: Path) -> None:
    (tmp_path / "full_text.txt").write_text("a" * 12000, encoding="utf-8")
    receipt = split_mod.split(tmp_path, chunk=5000, overlap=200)
    assert (receipt["chunks"], receipt["mode"]) == (3, "chars")
    assert len((tmp_path / "chunks" / "0000.txt").read_text(encoding="utf-8")) == 5000


def test_merged_and_per_doc_qa_reports(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    qa = _qa(tmp_path)
    work = tmp_path / "work"
    receipt = batch_mod.ingest(str(src), work, qa=qa, k=5)
    merged = json.loads((work / "qa-report.json").read_text(encoding="utf-8"))
    assert merged["k"] == 5 and merged["graded_on"] == "batch-chunks"
    assert (merged["total"], merged["passed"]) == (3, 2)
    assert abs(merged["rate"] - 2 / 3) < 1e-9
    assert receipt["qa"]["merged"]["passed"] == 2
    lines = (work / "qa-per-doc.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 2
    per = [json.loads(ln) for ln in lines]
    by_doc = {r["doc"]: r for r in per}
    assert by_doc["alpha.md"]["passed"] == 1  # only the leases question
    assert by_doc["beta.md"]["passed"] == 1  # only the objects question
    for row in per:
        assert row["k"] == 5 and row["total"] == 3
        assert 0.0 <= row["rate"] <= 1.0


def test_k5_retrieve_qa_honest_fallback_never_claims(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    work = tmp_path / "work"
    batch_mod.ingest(str(src), work)
    qa = tmp_path / "qa.jsonl"
    qa.write_text('{"q": "what about qqqqmissing?", "must": ["qqqqmissing"]}\n', encoding="utf-8")
    report = batch_mod.retrieve_qa(work, qa, k=5)
    assert (report["total"], report["passed"], report["rate"]) == (1, 0, 0.0)
    item = report["items"][0]
    assert item["passed"] is False and item["verdict"] == "insufficient-evidence"
    assert item["fallback"] == batch_mod.FALLBACK_TEXT
    assert "no answer claimed" in item["fallback"]
    # an empty index is honest too, not an exception
    empty = tmp_path / "empty"
    empty.mkdir()
    (empty / "chunks").mkdir()
    index_mod.build_index(empty)
    qa2 = tmp_path / "qa2.jsonl"
    qa2.write_text('{"q": "what guards queues?", "must": ["leases"]}\n', encoding="utf-8")
    report2 = batch_mod.retrieve_qa(empty, qa2, k=5)
    assert report2["passed"] == 0 and report2["items"][0]["verdict"] == "insufficient-evidence"


def test_retrieve_caps_at_k_and_filters_per_doc(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    work = tmp_path / "work"
    batch_mod.ingest(str(src), work, chunk=30, overlap=5)
    hits = batch_mod.retrieve(work, "leases batch queues", k=5)
    assert 0 < len(hits) <= 5
    hits2 = batch_mod.retrieve(work, "leases batch queues", k=1)
    assert len(hits2) == 1
    alpha_hits = batch_mod.retrieve(work, "leases", k=5, doc="alpha.md")
    assert alpha_hits, "the leases answer lives in alpha.md"
    assert all(h["file"] in {n for r in batch_mod.read_manifest(work) if r["doc"] == "alpha.md" for n in r["chunk_files"]} for h in alpha_hits)
    with pytest.raises(ValueError, match="not in"):
        batch_mod.retrieve(work, "leases", k=5, doc="nope.md")


def test_cli_batch_command_writes_all_artifacts(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    qa = _qa(tmp_path)
    work = tmp_path / "work"
    result = CliRunner().invoke(main, ["batch", "--in", str(src), "--work", str(work),
                                       "--qa", str(qa), "--chunk-mode", "sentences",
                                       "--window", "2", "--sent-overlap", "1", "--k", "5"])
    assert result.exit_code == 0, result.output
    assert "batch 2 docs" in result.output and "qa 2/3" in result.output and "receipt" in result.output
    for name in ("manifest.jsonl", "qa-report.json", "qa-per-doc.jsonl", "batch.json", "receipt.json", "index.jsonl"):
        assert (work / name).is_file(), name
    assert len(sorted((work / "chunks").glob("*.txt"))) >= 2
    assert len(sorted((work / "receipts").glob("*.json"))) == 2


def test_batch_misuse_is_a_usage_error_not_a_traceback(tmp_path: Path) -> None:
    src = _two_docs(tmp_path)
    runner = CliRunner()
    bad_mode = runner.invoke(main, ["batch", "--in", str(src), "--work", str(tmp_path / "w1"), "--chunk-mode", "words"])
    assert bad_mode.exit_code != 0 and "Traceback" not in bad_mode.output
    missing = runner.invoke(main, ["batch", "--in", str(tmp_path / "nope"), "--work", str(tmp_path / "w2")])
    assert missing.exit_code == 2 and "not found" in missing.output
    assert "Traceback" not in missing.output
    bad_qa = tmp_path / "bad.jsonl"
    bad_qa.write_text('{"question": "x", "answer": "y"}\n', encoding="utf-8")
    wrong = runner.invoke(main, ["batch", "--in", str(src), "--work", str(tmp_path / "w3"), "--qa", str(bad_qa)])
    assert wrong.exit_code == 2 and "--qa" in wrong.output
    assert not (tmp_path / "w3" / "manifest.jsonl").exists()
    with pytest.raises(ValueError, match="--chunk-mode words"):
        batch_mod.ingest(str(src), tmp_path / "w4", chunk_mode="words")


def test_batch_tool_has_zero_new_deps() -> None:
    """batch.py imports stdlib plus our own stages only; requirements.txt unchanged."""
    tree = ast.parse((Path(__file__).resolve().parent.parent / "book2skill" / "batch.py").read_text(encoding="utf-8"))
    allowed_top = {"fnmatch", "json", "os", "re", "pathlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] in allowed_top, alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            if node.level == 0:
                assert (node.module or "").split(".")[0] in allowed_top, node.module
                continue
            names = {a.name.split(".")[0] for a in node.names}
            assert node.level == 1 and names <= {"eval", "extract", "index", "split"}, names
    req = (Path(__file__).resolve().parent.parent / "requirements.txt").read_text(encoding="utf-8")
    assert "click" in req and "pytest" in req
