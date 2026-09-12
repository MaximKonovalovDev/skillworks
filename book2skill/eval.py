"""Eval stage: source-derived Q&A with pass-rate gate.

QA file is JSONL: {"q": "...", "must": ["word1", "word2"]}.
A question passes when every must-word appears in the top search hits.
Gate: pass rate below 0.6 refuses export. Diagnostic, not a model metric.
"""
from __future__ import annotations

import json
from pathlib import Path

from .index import search


def run_eval(workdir: Path, skilldir: Path, qa_path: Path) -> dict:
    results = []
    for line in qa_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
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
    print(json.dumps(report, indent=2))
    return report
