#!/usr/bin/env python3
"""dora-delivery: grade delivery speed and stability from the four DORA metrics.

Headless: no network, no prompts. Reads one JSON file with the four
metric numbers and writes one JSON file with the grade per metric plus
the overall grade.

Usage:
    python scripts/dora_delivery.py --input <path> --out <path>

The first word of stdout is the answer. Exit codes: 0 when the work is done, 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DESCRIPTION = "Use when grading delivery speed and stability with the four DORA metrics and capability checklist: deploy rate, lead time, failure share, restore time."

KEYS = ("deploy_per_week", "lead_hours", "fail_pct", "restore_hours")
ORDER = {"low": 0, "medium": 1, "high": 2, "elite": 3}


def grade_deploy(v: float) -> str:
    if v >= 7:
        return "elite"
    if v >= 1:
        return "high"
    if v >= 0.25:
        return "medium"
    return "low"


def grade_lead(h: float) -> str:
    if h < 24:
        return "elite"
    if h <= 168:
        return "high"
    if h <= 720:
        return "medium"
    return "low"


def grade_fail(p: float) -> str:
    if p <= 15:
        return "elite"
    if p <= 30:
        return "high"
    if p <= 45:
        return "medium"
    return "low"


def grade_restore(h: float) -> str:
    if h < 24:
        return "elite"
    if h <= 168:
        return "high"
    if h <= 720:
        return "medium"
    return "low"


def fail(msg: str) -> int:
    print(f"ERROR {msg}; nothing written")
    return 2


def work(args: argparse.Namespace) -> int:
    src = Path(args.input)
    out = Path(args.out)
    try:
        if out.exists() and out.is_dir():
            return fail(f"refused: --out is a directory: {out}")
        try:
            if out.resolve() == src.resolve():
                return fail(f"refused: --out is the input file: {out}")
        except OSError:
            pass
    except OSError as err:
        return fail(f"refused: bad path: {err}")
    if not src.is_file():
        return fail(f"input file missing: {src}")
    try:
        raw = src.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        return fail(f"input is not UTF-8 text: {src}")
    except OSError as err:
        return fail(f"cannot read input: {src}")
    try:
        data = json.loads(raw)
    except ValueError:
        return fail(f"input is not JSON: {src}")
    if not isinstance(data, dict):
        return fail("input JSON must be an object with deploy_per_week, lead_hours, fail_pct, restore_hours")
    for k in KEYS:
        if k not in data:
            return fail(f"input misses key {k}: need deploy_per_week, lead_hours, fail_pct, restore_hours")
    try:
        deploy = float(data["deploy_per_week"])
        lead = float(data["lead_hours"])
        fail_pct = float(data["fail_pct"])
        restore = float(data["restore_hours"])
    except (TypeError, ValueError):
        return fail("each metric must be a number: deploy_per_week, lead_hours, fail_pct, restore_hours")
    if not (deploy >= 0):
        return fail(f"deploy_per_week must be >= 0, got {data['deploy_per_week']}")
    if not (lead >= 0):
        return fail(f"lead_hours must be >= 0, got {data['lead_hours']}")
    if not (0 <= fail_pct <= 100):
        return fail(f"fail_pct must be 0 to 100, got {data['fail_pct']}")
    if not (restore >= 0):
        return fail(f"restore_hours must be >= 0, got {data['restore_hours']}")
    grades = {
        "deploy": grade_deploy(deploy),
        "lead": grade_lead(lead),
        "fail": grade_fail(fail_pct),
        "restore": grade_restore(restore),
    }
    overall = min(grades.values(), key=lambda g: ORDER[g])
    record = {
        "tool": "dora-delivery",
        "overall": overall,
        "deploy": grades["deploy"],
        "lead": grades["lead"],
        "fail": grades["fail"],
        "restore": grades["restore"],
        "input": {
            "deploy_per_week": deploy,
            "lead_hours": lead,
            "fail_pct": fail_pct,
            "restore_hours": restore,
        },
    }
    try:
        if out.parent and str(out.parent) not in ("", "."):
            out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    except OSError as err:
        return fail(f"cannot write output: {out}")
    print(f"GRADE {overall} deploy {grades['deploy']} lead {grades['lead']} fail {grades['fail']} restore {grades['restore']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a non-ASCII name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="input JSON file with deploy_per_week, lead_hours, fail_pct, restore_hours")
    parser.add_argument("--out", required=True, help="output JSON file for the grade record (created on success)")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())
