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
import warnings
from pathlib import Path

from .index import search

# Shop copy is not an answer: listing/vol0/demo/export never grade a QA pair.
_SKIP_NAMES = {"listing.md", "vol0-sample.md", "vol0_sample.md", "eval_report.json", ".lock.json"}
_SKIP_DIRS = {"demo", "export"}


# Donor: pyeve/cerberus@83f5dada (branch 1.3.x), licence ISC,
# https://github.com/pyeve/cerberus/blob/1.3.x/cerberus/validator.py,
# https://github.com/pyeve/cerberus/blob/1.3.x/cerberus/errors.py:
# (1) unknown-field gate allow_unknown=False + UNKNOWN_FIELD + purge_unknown
# as strict mode on Schema; (2) ErrorDefinition(code, rule) + collect-all
# ErrorList for whole-file QA validate. Idea ported fresh; no donor code copied.
class ErrorDefinition:
    """One error kind: machine code plus human rule."""
    def __init__(self, code: str, rule: str):
        self.code = code
        self.rule = rule

    def __repr__(self) -> str:
        return f"ErrorDefinition({self.code!r}, {self.rule!r})"


UNKNOWN_FIELD = ErrorDefinition("UNKNOWN_FIELD", "unknown")
MISSING_FIELD = ErrorDefinition("MISSING_FIELD", "required")
BAD_VALUE = ErrorDefinition("BAD_VALUE", "bad")
INVALID_JSON = ErrorDefinition("INVALID_JSON", "json")


class ErrorList(list):
    """Collect-all errors for one file run: file:line + code per entry."""


_QA_KEYS = {"q", "must"}


def _qa_line_errors(item: object, qa_path: Path, lineno: int) -> list[str]:
    """One QA line to file:line+code strings (empty when good)."""
    prefix = f"--qa {qa_path} line {lineno}"
    if not isinstance(item, dict):
        return [f"{prefix} [{BAD_VALUE.code}] must be {{\"q\", \"must\"}} (got {type(item).__name__})"]
    unknown = sorted(set(item) - _QA_KEYS)
    if unknown:
        got = ", ".join(sorted(item.keys()))
        return [f"{prefix} [{UNKNOWN_FIELD.code}] unknown field {unknown[0]!r} (got keys: {got})"]
    if "q" not in item or "must" not in item:
        got = ", ".join(sorted(item.keys()))
        return [f"{prefix} [{MISSING_FIELD.code}] must be {{\"q\", \"must\"}} (got keys: {got})"]
    if not isinstance(item["q"], str):
        qtype = type(item["q"]).__name__
        return [f"{prefix} [{BAD_VALUE.code}] \"q\" must be a question string (got {qtype})"]
    if not isinstance(item["must"], list):
        mtype = type(item["must"]).__name__
        return [f"{prefix} [{BAD_VALUE.code}] \"must\" must be a list of words (got {mtype})"]
    return []


def _check_item(item: object, qa_path: Path, lineno: int) -> None:
    """Refuse a QA line that is not a {"q", "must"} item."""
    if not isinstance(item, dict):
        raise ValueError(f"--qa {qa_path} line {lineno} must be {{\"q\", \"must\"}} (got {type(item).__name__})")
    unknown = sorted(set(item) - _QA_KEYS)
    if unknown:
        got = ", ".join(sorted(item.keys()))
        raise ValueError(f"--qa {qa_path} line {lineno} [{UNKNOWN_FIELD.code}] unknown field {unknown[0]!r} (got keys: {got})")
    if "q" not in item or "must" not in item:
        got = ", ".join(sorted(item.keys()))
        raise ValueError(f"--qa {qa_path} line {lineno} must be {{\"q\", \"must\"}} (got keys: {got})")
    if not isinstance(item["q"], str):
        raise ValueError(f"--qa {qa_path} line {lineno} \"q\" must be a question string (got {type(item['q']).__name__})")
    if not isinstance(item["must"], list):
        raise ValueError(f"--qa {qa_path} line {lineno} \"must\" must be a list of words (got {type(item['must']).__name__})")


def validate_qa_all(qa_path: Path) -> ErrorList:
    """Collect-all QA check: file:line+code per bad line, never raise-first."""
    errors = ErrorList()
    for lineno, raw in enumerate(qa_path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError as exc:
            errors.append(f"--qa {qa_path} line {lineno} [{INVALID_JSON.code}] must be {{\"q\", \"must\"}} (got invalid JSON: {exc.msg})")
            continue
        errors.extend(_qa_line_errors(item, qa_path, lineno))
    return errors


def validate_qa(qa_path: Path) -> None:
    """Refuse a QA file with a wrong-shaped line before any stage runs."""
    errors = validate_qa_all(qa_path)
    if errors:
        raise ValueError(errors[0])


# Donor: keleshev/schema (MIT, https://github.com/keleshev/schema):
# Schema/And/Or/Optional/Use idea ported fresh; no donor code copied.
class Optional:
    """Mark a dict key as optional for Schema."""
    def __init__(self, key: str):
        self.key = key


class Use:
    """Check a value with a predicate or converter (True when it works)."""
    def __init__(self, fn):
        self.fn = fn

    def check(self, value) -> bool:
        try:
            result = self.fn(value)
        except Exception:
            return False
        return result if isinstance(result, bool) else True


class And:
    """All sub-checks must match."""
    def __init__(self, *checks):
        self.checks = checks

    def check(self, value) -> bool:
        return all(_matches(c, value) for c in self.checks)


class Or:
    """At least one sub-check must match."""
    def __init__(self, *checks):
        self.checks = checks

    def check(self, value) -> bool:
        return any(_matches(c, value) for c in self.checks)


def _matches(spec, value) -> bool:
    """One spec against one value: type, literal, callable or helper."""
    if isinstance(spec, (And, Or, Use)):
        return spec.check(value)
    if isinstance(spec, type):
        if spec is int:
            return isinstance(value, int) and not isinstance(value, bool)
        return isinstance(value, spec)
    if callable(spec):
        try:
            return bool(spec(value))
        except Exception:
            return False
    return value == spec


class Schema:
    """Tiny dict validator returning file:line error strings."""
    def __init__(self, spec: dict, allow_unknown: bool = False, purge_unknown: bool = False):
        self.spec = spec
        self.allow_unknown = allow_unknown
        self.purge_unknown = purge_unknown

    def validate(self, record: object, fname: str) -> list[str]:
        if not isinstance(record, dict):
            return [f"{fname}:1: expected object (got {type(record).__name__})"]
        known = {k.key if isinstance(k, Optional) else k for k in self.spec}
        if self.purge_unknown and isinstance(record, dict):
            for key in [k for k in record if k not in known]:
                del record[key]
        errors: list[str] = []
        for raw_key, sub in self.spec.items():
            optional = isinstance(raw_key, Optional)
            key = raw_key.key if optional else raw_key
            if key not in record:
                if not optional:
                    errors.append(f"{fname}:1: missing {key} (counts incomplete)")
                continue
            if not _matches(sub, record[key]):
                errors.append(f"{fname}:1: bad {key}: {record[key]!r}")
        if not self.allow_unknown:
            for key in sorted(set(record) - known):
                errors.append(f"{fname}:1: {UNKNOWN_FIELD.code} unknown field {key!r}")
        return errors


def _is_int(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_num(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_rate(value) -> bool:
    return _is_num(value) and 0.0 <= float(value) <= 1.0


def _is_lift(value) -> bool:
    return _is_num(value) and -1.0 <= float(value) <= 1.0


def _is_hex64(value) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    return all(c in "0123456789abcdefABCDEF" for c in value)


def validate_receipt(record: object) -> list[str]:
    """Check an eval_report record; returns file:line errors (empty when good)."""
    fname = "eval_report.json"
    errors = Schema({
        "skill": Use(_nonempty_str),
        "total": And(Use(_is_int), Use(lambda n: _is_int(n) and n >= 0)),
        "passed": And(Use(_is_int), Use(lambda n: _is_int(n) and n >= 0)),
        "rate": Use(_is_rate),
        "graded_on": Or("skill", "work-chunks"),
    }, allow_unknown=False).validate(record, fname)
    if isinstance(record, dict) and _is_int(record.get("total")) and _is_int(record.get("passed")):
        total = record["total"]
        passed = record["passed"]
        if passed > total:
            errors.append(f"{fname}:1: passed {passed} > total {total}")
        rate = record.get("rate")
        if _is_num(rate):
            expected = (passed / total) if total else 0.0
            if abs(float(rate) - expected) > 1e-6:
                errors.append(f"{fname}:1: rate {rate!r} != passed/total {expected:.6f}")
    return errors


def validate_trial_proof(record: object) -> list[str]:
    """Check a trial-proof record; returns file:line errors (empty when good)."""
    fname = "trial-proof.json"
    errors = Schema({
        "runs": And(Use(_is_int), Use(lambda n: _is_int(n) and n >= 0)),
        "with_rate": Use(_is_rate),
        "without_rate": Use(_is_rate),
        "lift": Use(_is_lift),
        "spread": Use(_is_rate),
        "fingerprint": Use(_is_hex64),
    }, allow_unknown=False).validate(record, fname)
    if isinstance(record, dict):
        with_rate = record.get("with_rate")
        without_rate = record.get("without_rate")
        lift = record.get("lift")
        if _is_num(with_rate) and _is_num(without_rate) and _is_num(lift):
            expected = float(with_rate) - float(without_rate)
            try:
                if abs(float(lift) - expected) > 1e-3:
                    errors.append(f"{fname}:1: lift {lift!r} != with_rate-without_rate {expected:.4f}")
            except Exception:
                pass
    return errors


def grow_qa(chapter: str, limit: int = 5) -> list[dict]:
    """Grow source-derived QA from one chapter (dspy-signature pattern: idea only).

    The "signature" is the contract: question answerable from the chapter,
    must-words quoted verbatim from it. Returns {"q", "must"} items.
    """
    import re

    words = re.findall(r"[^\W\d_][^\W\d_-]{4,}", chapter)
    seen: dict[str, None] = {}
    for w in words:
        key = w.casefold()
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
    words = [w.casefold() for w in query.split() if len(w) > 2]
    lowered = [(name, text.casefold()) for name, text in texts]
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


# Idea from satchmakua/gatecheck (MIT): deterministic check ANDed with second grade + fault-injection negative control. Written fresh here, no donor code copied.
def _substantive(blob: str, must: list[str]) -> bool:
    import re
    if not must:
        return True
    words = re.findall(r"[^\W\d_]{3,}", blob)
    if len({w.casefold() for w in words}) < 5:
        return False
    sentences = re.findall("[^.!?]+[.!?]", blob)
    if not sentences:
        return False
    for m in must:
        hit = [s for s in sentences if m in s and len(re.findall(r"[^\W\d_]{3,}", s)) >= 3]
        if not hit:
            return False
    return True


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
        blob = blob.casefold()
        must = [w.casefold() for w in item.get("must", [])]
        passed = all(w in blob for w in must) and (graded_on != "skill" or _substantive(blob, must))
        results.append({"q": item["q"], "passed": passed})
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    rate = (passed / total) if total else 0.0
    report = {"skill": str(skilldir), "total": total, "passed": passed, "rate": rate,
              "graded_on": graded_on}
    for err in validate_receipt(report):
        warnings.warn(err)
    proof_path = skilldir / "references" / "trial-proof.json"
    if proof_path.exists():
        try:
            proof_record = json.loads(proof_path.read_text(encoding="utf-8"))
            for err in validate_trial_proof(proof_record):
                warnings.warn(err)
        except (OSError, ValueError) as exc:
            warnings.warn(f"trial-proof.json unreadable: {exc}")
    skilldir.mkdir(parents=True, exist_ok=True)
    (skilldir / "eval_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report
