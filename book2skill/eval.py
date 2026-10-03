"""Eval stage: source-derived Q&A with pass-rate gate.

QA file is JSONL: {"q": "...", "must": ["word1", "word2"]}.
A question passes when every must-word appears in the top search hits.
Gate: pass rate below 0.6 refuses export. Diagnostic, not a model metric.
"""
from __future__ import annotations

import json
from pathlib import Path

from .index import search


def _check_item(item: object, qa_path: Path, lineno: int) -> None:
    """Refuse a QA line that is not a {"q", "must"} item."""
    if (
        not isinstance(item, dict)
        or "q" not in item
        or "must" not in item
        or not isinstance(item["q"], str)
        or not isinstance(item["must"], list)
    ):
        got = ", ".join(sorted(item.keys())) if isinstance(item, dict) else type(item).__name__
        raise ValueError(f"--qa {qa_path} line {lineno} must be {{\"q\", \"must\"}} (got keys: {got})")


def validate_qa(qa_path: Path) -> None:
    """Refuse a QA file with a wrong-shaped line before any stage runs."""
    for lineno, raw in enumerate(qa_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"--qa {qa_path} line {lineno} must be {{\"q\", \"must\"}} (got invalid JSON: {exc.msg})") from None
        _check_item(item, qa_path, lineno)


def grow_qa(chapter: str, limit: int = 5) -> list[dict]:
    """Grow source-derived QA from one chapter (dspy-signature pattern: idea only).

    The "signature" is the contract: question answerable from the chapter,
    must-words quoted verbatim from it. Returns {"q", "must"} items.
    """
    import re

    words = re.findall(r"[A-Za-z][A-Za-z-]{4,}", chapter)
    seen: dict[str, None] = {}
    for w in words:
        key = w.lower()
        if key not in seen:
            seen[key] = None
    terms = list(seen)[:limit]
    return [
        {"q": f"what does the chapter say about {t}?", "must": [t]} for t in terms
    ]


def run_eval(workdir: Path, skilldir: Path, qa_path: Path) -> dict:
    results = []
    for lineno, raw in enumerate(qa_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"--qa {qa_path} line {lineno} must be {{\"q\", \"must\"}} (got invalid JSON: {exc.msg})") from None
        _check_item(item, qa_path, lineno)
        hits = search(workdir, item["q"], limit=5)
        blob = " ".join(
            (workdir / "chunks" / f"{h['file']}").read_text(encoding="utf-8").lower()
            for h in hits
        )
        must = [w.lower() for w in item.get("must", [])]
        passed = all(w in blob for w in must)
        results.append({"q": item["q"], "passed": passed})
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    rate = (passed / total) if total else 0.0
    report = {"skill": str(skilldir), "total": total, "passed": passed, "rate": rate}
    skilldir.mkdir(parents=True, exist_ok=True)
    (skilldir / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report
