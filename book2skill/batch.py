"""Batch ingest: many docs in, one merged chunk index out, with receipts.

One folder of docs (or one file) becomes merged chunks plus a manifest with
one row per doc, a merged QA report plus a per-doc QA report, and receipts.
Chunking reuses split.chunk_text (chars slices or sentence windows); ranking
reuses index.search (top-k); QA shape reuses eval.validate_qa. No new deps.

Layout under workdir:
  manifest.jsonl      one JSON per doc (doc, kind, chars, chunks, chunk_files)
  chunks/*.txt        merged chunks, each headed by "# doc: <rel>"
  index.jsonl         merged index over chunks
  qa-report.json      merged retrieve-QA report (k hits per question)
  qa-per-doc.jsonl    one JSON per doc with its own retrieve-QA report
  batch.json          merged receipt (also copied to receipt.json)
  receipts/<slug>.json  per-doc receipt (extract counts plus chunk files)
  per-doc/<slug>/     per-doc full_text.txt kept for inspection
"""
from __future__ import annotations

import fnmatch
import json
import os
import re
from pathlib import Path

from . import eval as eval_mod
from . import extract as extract_mod
from . import index as index_mod
from . import split as split_mod

MANIFEST = "manifest.jsonl"
BATCH_RECEIPT = "batch.json"
QA_REPORT = "qa-report.json"
QA_PER_DOC = "qa-per-doc.jsonl"
K_DEFAULT = 5
FALLBACK_TEXT = "insufficient evidence in top-5; no answer claimed"

_BATCH_SUFFIXES = tuple(sorted(set(extract_mod.DOC_SUFFIXES) | {".pdf", ".epub", ".docx"}))


def _slug(name: str, seen: set[str]) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "doc"
    slug, n = base, 2
    while slug in seen:
        slug = f"{base}-{n}"
        n += 1
    seen.add(slug)
    return slug


def _is_link(path: str) -> bool:
    isjunction = getattr(os.path, "isjunction", None)
    return os.path.islink(path) or bool(isjunction and isjunction(path))


def discover_docs(src: str, workdir: Path, include: str | None = None) -> list[tuple[Path, str]]:
    """Doc files under src in path order as (path, rel) pairs.

    A single file counts as one doc. A folder walks recursively, leaving out
    hidden folders, node_modules, __pycache__, export/ folders, links, and the
    work dir itself when it sits inside src (a rerun must not read its output).
    """
    if not os.path.exists(src):
        raise ValueError(f"--in {src} not found: give a file or a docs folder")
    path = Path(src)
    if path.is_file():
        return [(path, path.name)]
    root = path.resolve()
    own = Path(workdir).resolve()
    found: list[tuple[Path, str]] = []
    for here, dirs, files in os.walk(root):
        keep = []
        for d in sorted(dirs):
            full = os.path.join(here, d)
            try:
                resolved = Path(full).resolve()
            except OSError:
                continue
            if resolved == own or own in resolved.parents and resolved == own:
                continue
            if resolved == own:
                continue
            if str(own).startswith(str(resolved)) or str(resolved).startswith(str(own)):
                if resolved == own:
                    continue
            if d.startswith(".") or d in {"node_modules", "__pycache__", "export"} or _is_link(full):
                continue
            keep.append(d)
        dirs[:] = keep
        for name in sorted(files):
            if name.startswith("."):
                continue
            low = name.lower()
            if not low.endswith(_BATCH_SUFFIXES):
                continue
            full_path = Path(here) / name
            try:
                rel = full_path.resolve().relative_to(root).as_posix()
            except ValueError:
                rel = name
            try:
                if Path(full_path).resolve() == own or own in Path(full_path).resolve().parents:
                    continue
            except OSError:
                pass
            if str(full_path.resolve()).startswith(str(own) + os.sep):
                continue
            if include and not (fnmatch.fnmatch(name, include) or fnmatch.fnmatch(rel, include)):
                continue
            found.append((full_path, rel))
    if not found:
        raise ValueError(
            f"no {', '.join(_BATCH_SUFFIXES)} files under {root}" + (f" matching {include!r}" if include else "")
        )
    return sorted(found, key=lambda pair: pair[1])


def retrieve(workdir: Path, query: str, k: int = K_DEFAULT, doc: str | None = None) -> list[dict]:
    """Top-k chunk hits for one query, optionally only one manifest doc."""
    if k < 1:
        raise ValueError(f"batch: k {k} must be 1 or more")
    if doc is None:
        return index_mod.search(workdir, query, limit=k)
    manifest = read_manifest(workdir)
    wanted: set[str] | None = None
    for row in manifest:
        if row.get("doc") == doc:
            wanted = set(row.get("chunk_files", []))
            break
    if wanted is None:
        raise ValueError(f"batch: doc {doc!r} not in {workdir / MANIFEST}")
    total = len(list((workdir / "chunks").glob("*.txt"))) or k
    hits = index_mod.search(workdir, query, limit=max(total, k))
    return [h for h in hits if h.get("file") in wanted][:k]


def read_manifest(workdir: Path) -> list[dict]:
    """Manifest rows as dicts; empty list when no batch ran yet."""
    path = workdir / MANIFEST
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _grade_blob(workdir: Path, hits: list[dict], must: list[str]) -> tuple[bool, str]:
    """Honest grade: pass only when every must-word sits in the hit text."""
    if not hits:
        return False, FALLBACK_TEXT
    blob_parts = []
    for h in hits:
        try:
            blob_parts.append((workdir / "chunks" / str(h["file"])).read_text(encoding="utf-8"))
        except OSError:
            continue
    blob = " ".join(blob_parts).lower()
    if not blob.strip():
        return False, FALLBACK_TEXT
    low_must = [w.lower() for w in must]
    if all(w in blob for w in low_must):
        return True, ""
    return False, FALLBACK_TEXT


def retrieve_qa(workdir: Path, qa_path: Path, k: int = K_DEFAULT) -> dict:
    """Merged retrieve-QA over merged chunks with an honest fallback.

    Each question gets the top-k chunks; a question passes only when every
    must-word appears in them. Anything else is verdict insufficient-evidence
    with the fallback text, never a claimed answer. Writes qa-report.json.
    """
    if k < 1:
        raise ValueError(f"batch: k {k} must be 1 or more")
    eval_mod.validate_qa(Path(qa_path))
    items = []
    for lineno, raw in enumerate(Path(qa_path).read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        item = json.loads(line)
        hits = retrieve(workdir, item["q"], k=k)
        passed, fallback = _grade_blob(workdir, hits, item.get("must", []))
        entry: dict = {
            "q": item["q"],
            "passed": passed,
            "verdict": "pass" if passed else "insufficient-evidence",
            "hits": [h["file"] for h in hits],
        }
        if not passed:
            entry["fallback"] = fallback
        items.append(entry)
    total = len(items)
    passed = sum(1 for e in items if e["passed"])
    report = {
        "qa": str(qa_path),
        "k": k,
        "total": total,
        "passed": passed,
        "rate": (passed / total) if total else 0.0,
        "graded_on": "batch-chunks",
        "items": items,
    }
    (workdir / QA_REPORT).write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def retrieve_qa_per_doc(workdir: Path, qa_path: Path, k: int = K_DEFAULT) -> list[dict]:
    """Per-doc retrieve-QA: the same QA graded on each doc alone.

    Writes qa-per-doc.jsonl (one JSON per doc). Each doc row carries its own
    total/passed/rate plus per-question verdicts with the same honest fallback.
    """
    if k < 1:
        raise ValueError(f"batch: k {k} must be 1 or more")
    eval_mod.validate_qa(Path(qa_path))
    manifest = read_manifest(workdir)
    if not manifest:
        raise ValueError(f"batch: {workdir / MANIFEST} missing: run batch ingest first")
    qa_items = [json.loads(ln) for ln in Path(qa_path).read_text(encoding="utf-8").splitlines() if ln.strip()]
    rows = []
    for m in manifest:
        doc = m["doc"]
        items = []
        for item in qa_items:
            hits = retrieve(workdir, item["q"], k=k, doc=doc)
            passed, fallback = _grade_blob(workdir, hits, item.get("must", []))
            entry: dict = {
                "q": item["q"],
                "passed": passed,
                "verdict": "pass" if passed else "insufficient-evidence",
                "hits": [h["file"] for h in hits],
            }
            if not passed:
                entry["fallback"] = fallback
            items.append(entry)
        total = len(items)
        passed = sum(1 for e in items if e["passed"])
        rows.append({
            "doc": doc,
            "k": k,
            "total": total,
            "passed": passed,
            "rate": (passed / total) if total else 0.0,
            "graded_on": "batch-chunks-per-doc",
            "items": items,
        })
    with (workdir / QA_PER_DOC).open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return rows


def ingest(src: str, workdir: Path, chunk_mode: str = "chars", chunk: int = split_mod.CHUNK,
           overlap: int = split_mod.OVERLAP, window: int = split_mod.SENTENCE_WINDOW,
           sent_overlap: int = split_mod.SENTENCE_OVERLAP, include: str | None = None,
           engine: str = "classic", k: int = K_DEFAULT, qa: Path | None = None) -> dict:
    """Batch-ingest src (a file or a docs folder) into merged chunks plus reports."""
    if chunk_mode not in split_mod.CHUNK_MODES:
        raise ValueError(f"--chunk-mode {chunk_mode} unknown: pick chars or sentences")
    if k < 1:
        raise ValueError(f"--k {k} must be 1 or more")
    if qa is not None:
        eval_mod.validate_qa(Path(qa))
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    docs = discover_docs(src, workdir, include=include)
    chunk_dir = workdir / "chunks"
    chunk_dir.mkdir(exist_ok=True)
    for stale in chunk_dir.glob("*.txt"):
        stale.unlink()
    per_doc_root = workdir / "per-doc"
    receipts_dir = workdir / "receipts"
    receipts_dir.mkdir(exist_ok=True)
    for stale in receipts_dir.glob("*.json"):
        stale.unlink()

    manifest_rows: list[dict] = []
    seen: set[str] = set()
    counter = 0
    for doc_path, rel in docs:
        slug = _slug(Path(rel).stem, seen)
        per_doc_work = per_doc_root / slug
        per_doc_work.mkdir(parents=True, exist_ok=True)
        extract_receipt = extract_mod.extract(str(doc_path), per_doc_work, engine=engine)
        text = (per_doc_work / "full_text.txt").read_text(encoding="utf-8")
        pieces = split_mod.chunk_text(text, mode=chunk_mode, chunk=chunk, overlap=overlap,
                                      window=window, sent_overlap=sent_overlap)
        if not pieces or not text.strip():
            raise ValueError(f"batch: {doc_path} yielded no text: nothing to chunk")
        chunk_files: list[str] = []
        for piece in pieces:
            name = f"{counter:04d}.txt"
            (chunk_dir / name).write_text(f"# doc: {rel}\n\n{piece}", encoding="utf-8")
            chunk_files.append(name)
            counter += 1
        row = {
            "doc": rel,
            "slug": slug,
            "source": str(doc_path),
            "kind": extract_receipt.get("kind", "text"),
            "chars": len(text),
            "chunks": len(pieces),
            "chunk_files": chunk_files,
            "mode": chunk_mode,
        }
        manifest_rows.append(row)
        per_doc_receipt = {
            "stage": "batch-doc",
            "doc": rel,
            "slug": slug,
            "kind": row["kind"],
            "chars": row["chars"],
            "chunks": row["chunks"],
            "chunk_files": chunk_files,
            "engine": extract_receipt.get("engine", engine),
        }
        (receipts_dir / f"{slug}.json").write_text(json.dumps(per_doc_receipt, indent=2), encoding="utf-8")
    with (workdir / MANIFEST).open("w", encoding="utf-8") as fh:
        for row in manifest_rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    index_receipt = index_mod.build_index(workdir)
    qa_merged: dict | None = None
    qa_docs: list[dict] | None = None
    if qa is not None:
        qa_merged = retrieve_qa(workdir, Path(qa), k=k)
        qa_docs = retrieve_qa_per_doc(workdir, Path(qa), k=k)
    receipt: dict = {
        "stage": "batch",
        "source": str(src),
        "docs": len(manifest_rows),
        "chunks": counter,
        "records": index_receipt.get("records", 0),
        "chunk_mode": chunk_mode,
        "chunk": chunk,
        "overlap": overlap,
        "k": k,
        "manifest": MANIFEST,
        "engine": engine,
    }
    if chunk_mode == "sentences":
        receipt["window"] = window
        receipt["sent_overlap"] = sent_overlap
    if qa_merged is not None:
        assert qa_docs is not None
        receipt["qa"] = {
            "merged": {"total": qa_merged["total"], "passed": qa_merged["passed"], "rate": qa_merged["rate"]},
            "per_doc": [{"doc": r["doc"], "total": r["total"], "passed": r["passed"], "rate": r["rate"]} for r in qa_docs],
            "k": k,
        }
    (workdir / BATCH_RECEIPT).write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    (workdir / "receipt.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    return receipt
