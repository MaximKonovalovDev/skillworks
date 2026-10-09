#!/usr/bin/env python3
"""netcode-patterns: check a netcode message plan for send flags and terms.

Headless: no network, no prompts. Reads one plan.json file from --input,
checks each message, and writes report.json into the --out folder.

Usage:
    python scripts/netcode_patterns.py --input <path> --out <path>

The first word of stdout is the answer. Exit codes: 0 when the work is done, 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

DESCRIPTION = "Check a netcode message plan for send flags, connection states and P2P terms before it ships. Use when choosing GameNetworkingSockets send flags or reviewing a multiplayer message plan."

NAME_RE = re.compile(r"^[a-z0-9_]{1,32}$")


def flag_for(delivery: str, urgent: bool) -> str:
    if delivery == "reliable":
        return "ReliableNoNagle" if urgent else "Reliable"
    return "UnreliableNoNagle" if urgent else "Unreliable"


def plan_problem(plan: object) -> str | None:
    if not isinstance(plan, dict):
        return "top value must be an object with a messages list"
    if "messages" not in plan:
        return "missing messages list"
    messages = plan["messages"]
    if not isinstance(messages, list):
        return "messages must be a list"
    seen: set[str] = set()
    for i, item in enumerate(messages):
        where = f"message {i}"
        if not isinstance(item, dict):
            return f"{where} must be an object"
        name = item.get("name")
        if not isinstance(name, str) or not NAME_RE.match(name):
            return f"{where} has bad name {name!r}: use [a-z0-9_] 1-32 chars"
        if name in seen:
            return f"duplicate name {name!r}: names must be unique"
        seen.add(name)
        delivery = item.get("delivery")
        if delivery not in ("reliable", "unreliable"):
            return f"{name} has bad delivery {delivery!r}: use reliable or unreliable in lower case"
        urgent = item.get("urgent")
        if type(urgent) is not bool:
            return f"{name} has bad urgent {urgent!r}: use true or false"
        size = item.get("size")
        if type(size) is not int or not 1 <= size <= 524288:
            return f"{name} has bad size {size!r}: use 1 to 524288"
        rate = item.get("per_second")
        if type(rate) is bool or not isinstance(rate, (int, float)):
            return f"{name} has bad per_second {rate!r}: use a number over 0 at most 120"
        if not isinstance(rate, bool):
            try:
                ok = math.isfinite(float(rate)) and float(rate) > 0 and float(rate) <= 120
            except (ValueError, OverflowError):
                ok = False
            if not ok:
                return f"{name} has bad per_second {rate!r}: use a number over 0 at most 120"
    return None


def work(args: argparse.Namespace) -> int:
    src = Path(args.input)
    out = Path(args.out)
    try:
        same = src.resolve() == out.resolve()
    except OSError:
        same = False
    if same:
        print(f"ERROR refused: --out is the input file: {out}; nothing written")
        return 2
    if out.is_file():
        print(f"ERROR refused: --out is a file: {out}; nothing written")
        return 2
    if not src.is_file():
        print(f"ERROR input file missing: {src}; nothing written")
        return 2
    try:
        raw = src.read_bytes().decode("utf-8")
    except UnicodeDecodeError:
        print(f"ERROR input is not UTF-8: {src}; nothing written")
        return 2
    except OSError as err:
        print(f"ERROR cannot read input: {src}: {err.strerror}; nothing written")
        return 2
    try:
        plan = json.loads(raw)
    except json.JSONDecodeError as err:
        print(f"ERROR input is not JSON: {src}: {err.msg}; nothing written")
        return 2
    problem = plan_problem(plan)
    if problem is not None:
        print(f"ERROR bad plan: {problem}; nothing written")
        return 2
    messages = plan["messages"]
    flags: dict[str, str] = {}
    warnings: list[str] = []
    for item in messages:
        name = item["name"]
        delivery = item["delivery"]
        urgent = item["urgent"]
        size = item["size"]
        rate = item["per_second"]
        flags[name] = flag_for(delivery, urgent)
        if size > 1200:
            warnings.append(f"{name}: size {size} may fragment")
        if delivery == "reliable" and float(rate) > 20:
            warnings.append(f"{name}: reliable at {rate}/s")
    n = len(messages)
    m = len(flags)
    w = len(warnings)
    report = {"tool": "netcode-patterns", "messages": n, "flags": flags, "warnings": warnings}
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report) + "\n", encoding="utf-8")
    print(f"RUN {n} messages flags {m} warnings {w}")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a non-ASCII name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="plan.json file to check")
    parser.add_argument("--out", required=True, help="folder that will hold report.json")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())
