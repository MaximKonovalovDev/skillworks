#!/usr/bin/env python3
"""staff-plus-operating: a fleet skill script.

Headless: no network, no prompts. Reads one JSON brief from --input
and writes one markdown operating report to --out.

Usage:
    python scripts/staff_plus_operating.py --input <brief.json> --out <report.md>

The first word of stdout is the answer. Exit codes: 0 when the work is done, 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

DESCRIPTION = "Operate as a staff-plus engineer with four archetypes plus a weekly checklist plus a decision record. Use when leading technical direction, staffing a hard problem, or writing a reviewable decision without a manager title."

SCOPES = ("team", "multi-team", "single-hard-problem", "leader-support")
SCOPE_TO_ARCHETYPE = {
    "team": "tech-lead",
    "multi-team": "architect",
    "single-hard-problem": "solver",
    "leader-support": "right-hand",
}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(message: str) -> int:
    print(f"ERROR {message}; nothing written")
    return 2


def work(args: argparse.Namespace) -> int:
    src = Path(args.input)
    out = Path(args.out)
    try:
        if out.resolve() == src.resolve():
            return fail(f"refused: --out is the input file: {out}")
    except OSError:
        pass
    if not src.is_file():
        return fail(f"input missing: {src}")
    try:
        raw = src.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return fail(f"input is not UTF-8 text: {src}")
    except OSError as err:
        return fail(f"cannot read input: {src} ({err.strerror})")
    try:
        data = json.loads(raw)
    except ValueError:
        return fail(f"input is not JSON: {src}")
    if not isinstance(data, dict):
        return fail(f"input must be a JSON object: {src}")

    title = data.get("title")
    situation = data.get("situation")
    scope = data.get("scope")
    options = data.get("options")
    owner = data.get("owner")
    review_date = data.get("review_date")
    risks = data.get("risks", [])
    context = data.get("context", "")

    if not isinstance(title, str) or not title.strip():
        return fail("bad title: give a non-empty string")
    if len(title.strip()) > 120:
        return fail("bad title: keep it to 120 characters or less")
    if not isinstance(situation, str) or not situation.strip():
        return fail("bad situation: give a non-empty string")
    if scope not in SCOPES:
        return fail(f"bad scope: want one of {", ".join(SCOPES)}")
    if not isinstance(options, list) or len([o for o in options if isinstance(o, str) and o.strip()]) < 2:
        return fail("bad options: list at least 2 non-empty strings")
    if not isinstance(owner, str) or not owner.strip():
        return fail("bad owner: give a non-empty string")
    if not isinstance(review_date, str) or not DATE_RE.match(review_date):
        return fail("bad review_date: want YYYY-MM-DD")
    if not isinstance(risks, list) or not all(isinstance(r, str) for r in risks):
        return fail("bad risks: want a list of strings")
    if context is None:
        context = ""
    if not isinstance(context, str):
        return fail("bad context: want a string")

    archetype = SCOPE_TO_ARCHETYPE[scope]
    clean_options = [o.strip() for o in options if isinstance(o, str) and o.strip()]
    clean_risks = [r.strip() for r in risks if r.strip()]

    checks = [
        ("direction-written", bool(title.strip() and situation.strip())),
        ("owner-named", bool(owner.strip())),
        ("options-listed", len(clean_options) >= 2),
        ("risks-listed", len(clean_risks) >= 1),
        ("review-dated", bool(DATE_RE.match(review_date))),
        ("scope-matched", scope in SCOPES),
    ]
    passed = sum(1 for _, ok in checks if ok)

    lines = []
    lines.append(f"# Decision: {title.strip()}")
    lines.append("")
    lines.append(f"archetype: {archetype}")
    lines.append(f"scope: {scope}")
    lines.append(f"owner: {owner.strip()}")
    lines.append(f"review-date: {review_date}")
    lines.append("")
    lines.append("## Situation")
    lines.append("")
    lines.append(situation.strip())
    if context.strip():
        lines.append("")
        lines.append("## Context")
        lines.append("")
        lines.append(context.strip())
    lines.append("")
    lines.append("## Checklist")
    lines.append("")
    for name, ok in checks:
        mark = "x" if ok else " "
        word = "PASS" if ok else "FAIL"
        lines.append(f"- [{mark}] {name} {word}")
    lines.append("")
    lines.append("## Options")
    lines.append("")
    for i, opt in enumerate(clean_options, 1):
        lines.append(f"{i}. {opt}")
    lines.append("")
    lines.append("## Risks")
    lines.append("")
    if clean_risks:
        for risk in clean_risks:
            lines.append(f"- {risk}")
    else:
        lines.append("- none listed")
    lines.append("")
    lines.append("## Choice")
    lines.append("")
    lines.append("Fill this after review: choice, reasons, and follow-up.")
    lines.append("")
    report = "\n".join(lines) + "\n"

    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8", newline="\n")
    except OSError as err:
        return fail(f"cannot write output: {out} ({err.strerror})")
    print(f"OPERATE {archetype} checklist {passed}/6 decision {title.strip()}")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="JSON brief file with title, situation, scope, options, owner, review_date")
    parser.add_argument("--out", required=True, help="markdown report file to write")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())
