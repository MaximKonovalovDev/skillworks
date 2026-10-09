#!/usr/bin/env python3
"""flax-forge-ops: check a Forge lanes plan before it ships.

Headless: no network, no prompts. Reads one plan JSON file from --input,
checks lane names against the ten gateway lanes, and writes report.json
into the --out folder.

Usage:
    python scripts/flax_forge_ops.py --input <path> --out <path>

The first word of stdout is the answer. Exit codes: 0 when the work is done, 2 on bad input.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DESCRIPTION = "Operate the Forge AI game factory and Flax MCP bridge: gateway lanes, batch queues, MCP proxy, build and verify lanes. Use when working with Forge gateway, Flax tools, or factory sidecars."

KNOWN = ("chat", "vision", "embed", "image", "3d", "audio", "music", "tts", "stt", "world")

def plan_problem(plan: object) -> str | None:
    if not isinstance(plan, dict):
        return "top value must be an object with a lanes list"
    if "lanes" not in plan:
        return "missing lanes list"
    lanes = plan["lanes"]
    if not isinstance(lanes, list):
        return "lanes must be a list"
    if not lanes:
        return "lanes must hold at least one lane"
    seen: set[str] = set()
    for i, item in enumerate(lanes):
        where = f"lane {i}"
        if not isinstance(item, dict):
            return f"{where} must be an object"
        name = item.get("name")
        if not isinstance(name, str):
            return f"{where} has bad name {name!r}: use one of chat vision embed image 3d audio music tts stt world"
        low = name.lower()
        if low not in KNOWN:
            return f"{where} has bad name {name!r}: use one of chat vision embed image 3d audio music tts stt world"
        if low in seen:
            return f"duplicate lane {name!r}: names must be unique"
        seen.add(low)
    return None


def work(args: argparse.Namespace) -> int:
    src = Path(args.input)
    out = Path(args.out)
    try:
        same = src.resolve() == out.resolve()
    except OSError:
        same = False
    if same:
        print(f"ERROR refused: --out is the input path: {out}; nothing written")
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
    lanes = plan["lanes"]
    names = [str(item["name"]).lower() for item in lanes]
    n = len(names)
    report = {"tool": "flax-forge-ops", "lanes": n, "names": sorted(names)}
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report) + "\n", encoding="utf-8")
    print(f"RUN {n} lanes checked")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="lanes plan JSON file to check")
    parser.add_argument("--out", required=True, help="folder that will hold report.json")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())
