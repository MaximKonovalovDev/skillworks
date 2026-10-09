# Donor: lyncar98/agent-eval-harness (MIT), registry.py grader-registry idea,
# https://github.com/lyncar98/agent-eval-harness: named graders with id+version
# looked up identically from YAML/CLI/Python, unknown names fail loudly.
# Idea ported fresh here; no donor code copied.
"""Eval grader registry: named substring + negative-control graders."""
from __future__ import annotations

from collections.abc import Callable

GradeFn = Callable[[str, list[str]], bool]


def code_contains(answer: str, must: list[str]) -> bool:
    """Substring grade: every must-word appears in the answer blob."""
    blob = answer.lower()
    return all(w.lower() in blob for w in must)


def neg_control(answer: str, must: list[str]) -> bool:
    """Negative control: substring grade AND a 5-word substantive blob."""
    import re

    if not code_contains(answer, must):
        return False
    words = re.findall(r"[A-Za-z]{3,}", answer)
    return len({w.lower() for w in words}) >= 5


_GRADERS: dict[str, dict] = {}


def register_grader(grader_id: str, version: str, fn: GradeFn) -> dict:
    """Register one grader; returns its {id, version} stamp."""
    entry = {"id": grader_id, "version": version, "fn": fn}
    _GRADERS[grader_id] = entry
    return {"id": grader_id, "version": version}


register_grader("code_contains", "1", code_contains)
register_grader("neg_control", "1", neg_control)


def lookup(spec: str) -> dict:
    """Resolve a grader name from YAML/CLI/Python identically; fail loudly."""
    key = str(spec).strip()
    if key not in _GRADERS:
        known = ", ".join(sorted(_GRADERS))
        raise KeyError(f"unknown grader {key!r} (known: {known})")
    return _GRADERS[key]


def grade_with(grader_id: str, answer: str, must: list[str]) -> dict:
    """Grade one answer; receipt records the grader id+version used."""
    entry = lookup(grader_id)
    passed = bool(entry["fn"](answer, must))
    return {"passed": passed, "grader": entry["id"], "version": entry["version"]}
