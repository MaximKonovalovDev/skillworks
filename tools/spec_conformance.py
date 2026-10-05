"""Spec conformance: does one skill match the spec layout (SK-08).

Validates one SKILL.md (frontmatter, chapters, eval report beside the
skill) against the local gate rules. The rules mirror the spec template
shape this repo documents in README ("Skill layout") and the budgets in
book2skill/gates.py check_format/check_sources (read-only ideas: kebab
name, description budget plus Use-when trigger, licence line, body token
budget, ASCII, referenced files exist). No spec text is vendored here;
only the bar (field names and limits) is reimplemented.

Licences: anthropics/skills is idea-only (validate shape, never copy its
scripts); stdlib parsing only (no ebooklib); normalize ideas live in
tools/gutenberg_normalize.py (MIT idea, own code).

Command::

    python tools/spec_conformance.py --skill skills/<name> [--evals-dir evals]

Prints one PASS/FAIL line per check and ends with one RESULT line.
Exit 0 only on PASS.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TRIGGER_RE = re.compile(r"\bUse (when|before|whenever|for)\b")
REF_RE = re.compile(r"`((?:references|scripts)/[\w./-]+)`")
ABS_RE = re.compile(r"(?:[A-Za-z]:[\\/]|/(?:home|root|tmp|etc)/|Users[\\/]me\b)")

BODY_TOKEN_BUDGET = 2000
BODY_LINE_BUDGET = 500
DESC_MIN, DESC_MAX = 40, 1024
EVAL_MIN_RATE = 0.6  # the export gate; fleet skills use a stricter 0.9


def parse_frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^([\w-]+):\s*(.*)$", line)
        if kv:
            out[kv.group(1)] = kv.group(2).strip().strip('"')
    return out


def body_of(text: str) -> str:
    return re.sub(r"^---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)


def check(skilldir: Path, evals_dir: Path | None = None) -> dict:
    findings: list[tuple[str, str]] = []

    def say(ok: bool, what: str) -> None:
        findings.append(("PASS" if ok else "FAIL", what))

    name = skilldir.name
    md = skilldir / "SKILL.md"
    if not md.is_file():
        say(False, "SKILL.md missing")
        return {"ok": False, "findings": findings, "skill": name}
    say(True, "SKILL.md present")

    text = md.read_text(encoding="utf-8")
    fm = parse_frontmatter(text)
    if not fm:
        say(False, "frontmatter block missing")
    else:
        say(True, "frontmatter block present")

    say(fm.get("name") == name, f"name {fm.get('name')!r} must equal the folder")
    say(bool(NAME_RE.match(name)) and len(name) <= 64, "name is kebab-case, 64 chars or less")

    desc = fm.get("description", "")
    say(DESC_MIN <= len(desc) <= DESC_MAX, f"description is {len(desc)} chars, want {DESC_MIN}-{DESC_MAX}")
    say(bool(TRIGGER_RE.search(desc)), "description states when to use it (Use when/before/whenever/for)")

    say(bool(fm.get("license")), "licence line present")

    body = body_of(text)
    say(len(body.splitlines()) <= BODY_LINE_BUDGET, f"body {len(body.splitlines())} lines, budget {BODY_LINE_BUDGET}")
    say(len(body) // 4 + 10 <= BODY_TOKEN_BUDGET, "body within token budget")
    bad = sorted({c for c in text if ord(c) > 126})
    say(not bad, "plain ASCII" if not bad else f"non-ASCII characters {bad[:5]}")

    missing = [rel for rel in sorted(set(REF_RE.findall(text))) if not (skilldir / rel).exists()]
    say(not missing, "every named file exists" if not missing else f"named but missing: {missing[:3]}")
    say(not ABS_RE.search(text), "relative paths only")

    chapters = skilldir / "chapters"
    notes = sorted(chapters.glob("*.md")) if chapters.is_dir() else []
    say(bool(notes), "chapters/ holds notes" if notes else "chapters/ with notes missing")

    rate: float | None = None
    report = skilldir / "eval_report.json"
    if report.is_file():
        try:
            data = json.loads(report.read_text(encoding="utf-8"))
            rate = float(data.get("rate", -1))
            ok_eval = data.get("total", 0) >= 1 and rate >= EVAL_MIN_RATE
            say(ok_eval, f"eval report beside skill: rate {rate:.3f}" if rate >= 0 else "eval report has no rate")
        except (ValueError, TypeError, OSError) as exc:
            say(False, f"eval report unreadable ({exc})")
    else:
        base = evals_dir
        if base is None:
            root = skilldir.parent.parent if skilldir.parent.name == "skills" else skilldir.parent
            base = root / "evals"
        qa = base / f"{name}_qa.jsonl"
        if qa.is_file():
            rows = [ln for ln in qa.read_text(encoding="utf-8").splitlines() if ln.strip()]
            say(len(rows) >= 1, f"eval report beside skill: {len(rows)} QA rows in evals/")
        else:
            say(False, "eval report beside skill missing (eval_report.json or evals/<name>_qa.jsonl)")

    ok = all(level == "PASS" for level, _ in findings)
    return {"ok": ok, "findings": findings, "skill": name, "rate": rate}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skill", required=True, help="skill dir, e.g. skills/mybook")
    ap.add_argument("--evals-dir", default=None, help="evals dir, default <repo>/evals")
    args = ap.parse_args(argv)
    report = check(Path(args.skill), Path(args.evals_dir) if args.evals_dir else None)
    for level, what in report["findings"]:
        print(f"{level} {what}")
    print(f"skill {report['skill']}, checks {len(report['findings'])}")
    print("RESULT PASS" if report["ok"] else "RESULT FAIL")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
