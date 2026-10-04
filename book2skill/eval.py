"""Eval stage: the SKILL answers, not its source chunks.

QA file is JSONL: {"q": "...", "must": ["word1", "word2"]}.
A question passes only when every must-word appears in the top hits ranked
from the skill's own answer text (SKILL.md, chapters, glossary, patterns,
cheatsheet, references). A skill whose text was gutted fails even when the
work chunks still hold the answer: grade the skill, never the source.
Gate: pass rate below 0.6 refuses export. Diagnostic, not a model metric.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from .index import search

# Shop copy is not an answer: listing/vol0/demo/export never grade a QA pair.
_SKIP_NAMES = {"listing.md", "vol0-sample.md", "vol0_sample.md", "eval_report.json", ".lock.json"}
_SKIP_DIRS = {"demo", "export"}


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


def skill_answer_texts(skilldir: Path) -> list[tuple[str, str]]:
    """The skill's own answer text: (relative name, text) per markdown file.

    SKILL.md, chapters, glossary, patterns, cheatsheet and references answer
    questions; shop copy (listing, vol0 sample, demo), exports, lock files and
    the eval report itself never do.
    """
    out: list[tuple[str, str]] = []
    for path in sorted(skilldir.rglob("*.md")):
        try:
            rel = path.relative_to(skilldir)
        except ValueError:
            continue
        if path.name in _SKIP_NAMES or path.name.startswith("."):
            continue
        if any(part in _SKIP_DIRS or part.startswith(".") for part in rel.parts[:-1]):
            continue
        try:
            out.append((rel.as_posix(), path.read_text(encoding="utf-8")))
        except OSError:
            continue
    return out


def _rank(texts: list[tuple[str, str]], query: str, limit: int = 5) -> list[tuple[str, str]]:
    """Rarity-weighted substring rank over (name, text) pairs.

    Same formula as book2skill/index.py search (kept local so this module
    never reads the work chunks): weight(w) = log((N+1)/(df+1)) + 1, score =
    sum of count * weight. A question whose words match no skill file ranks
    nothing, so its must-words cannot pass.
    """
    words = [w.lower() for w in query.split() if len(w) > 2]
    lowered = [(name, text.lower()) for name, text in texts]
    total = len(lowered)
    weights = {}
    for w in words:
        df = sum(1 for _, text in lowered if w in text)
        weights[w] = math.log((total + 1) / (df + 1)) + 1.0
    scored = []
    for (name, _), (_, text) in zip(texts, lowered):
        score = sum(text.count(w) * weights[w] for w in words)
        if score:
            scored.append((score, name, text))
    scored.sort(reverse=True)
    return [(name, text) for _, name, text in scored[:limit]]


def run_eval(workdir: Path, skilldir: Path, qa_path: Path) -> dict:
    texts = skill_answer_texts(skilldir)
    # Legacy staged flow (book2skill/gates.py check_eval): the skill dir holds
    # no answer files because the skill text was staged as work chunks for
    # grading. Only then do the chunks grade, never beside a real skill.
    graded_on = "skill" if texts else "work-chunks"
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
        if graded_on == "skill":
            blob = " ".join(text for _, text in _rank(texts, item["q"], limit=5))
        else:
            hits = search(workdir, item["q"], limit=5)
            blob = " ".join(
                (workdir / "chunks" / f"{h['file']}").read_text(encoding="utf-8")
                for h in hits
            )
        blob = blob.lower()
        must = [w.lower() for w in item.get("must", [])]
        passed = all(w in blob for w in must)
        results.append({"q": item["q"], "passed": passed})
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    rate = (passed / total) if total else 0.0
    report = {"skill": str(skilldir), "total": total, "passed": passed, "rate": rate,
              "graded_on": graded_on}
    skilldir.mkdir(parents=True, exist_ok=True)
    (skilldir / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report
