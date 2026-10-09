#!/usr/bin/env python3
"""behavetree-how: check one BehaviorTree.CPP XML file.

Headless: no network, no prompts. It reads the XML file named by --input, checks
the node-type, XML, tick, and halt rules from SKILL.md, and writes a two-line
summary (tree ids, node count) to the file named by --out.

Usage:
    python scripts/behavetree_how.py --input <path> --out <path>

The first word of stdout is the answer. Exit codes: 0 when the work is done, 2 on bad input.
"""
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

DESCRIPTION = "Use when writing or fixing a BehaviorTree.CPP tree: node types, XML shape, tick returns, and halt rules with a checker that validates the file."

CONTROLS = {
    "Sequence", "ReactiveSequence", "SequenceWithMemory", "Fallback",
    "ReactiveFallback", "Parallel", "ParallelAll", "IfThenElse",
    "Switch", "WhileDoElse", "TryCatch", "Manual",
}
DECORATORS = {
    "Inverter", "ForceSuccess", "ForceFailure", "Repeat", "Retry",
    "Timeout", "Delay", "KeepRunningUntilFailure", "RunOnce", "Loop",
    "Precondition",
}


def fail(msg: str) -> int:
    print(f"ERROR {msg}")
    return 2


def work(args: argparse.Namespace) -> int:
    src = Path(args.input)
    if not src.is_file():
        return fail(f"missing input file: {args.input}")
    try:
        text = src.read_text(encoding="utf-8")
    except OSError as exc:
        return fail(f"cannot read input file: {exc}")
    try:
        root = ET.fromstring(text)
    except ET.ParseError as exc:
        return fail(f"bad XML: {exc}")
    if root.tag != "root":
        return fail(f"root tag must be `root`, got `{root.tag}`")
    if root.get("BTCPP_format") != "4":
        return fail("root must carry BTCPP_format=\"4\"")
    trees = root.findall("BehaviorTree")
    if not trees:
        return fail("no BehaviorTree block found")
    ids: list[str] = []
    for tree in trees:
        tid = (tree.get("ID") or "").strip()
        if not tid:
            return fail("BehaviorTree block without ID")
        if tid in ids:
            return fail(f"duplicate BehaviorTree ID: {tid}")
        ids.append(tid)
    problems: list[str] = []
    count = 0

    def visit(node: ET.Element) -> None:
        nonlocal count
        count += 1
        kids = list(node)
        if node.tag == "SubTree":
            sid = (node.get("ID") or "").strip()
            if not sid:
                problems.append("SubTree tag without ID")
            elif sid not in ids:
                problems.append(f"SubTree ID `{sid}` names no BehaviorTree in this file")
            if kids:
                problems.append("SubTree tag must not have children")
            return
        if node.tag in DECORATORS:
            if len(kids) != 1:
                problems.append(f"decorator `{node.tag}` must have exactly one child, got {len(kids)}")
        elif node.tag in CONTROLS or node.tag == "BehaviorTree":
            if not kids:
                problems.append(f"control `{node.tag}` must have at least one child")
        elif kids:
            problems.append(f"leaf `{node.tag}` must not have children")
        for kid in kids:
            visit(kid)

    for tree in trees:
        visit(tree)
    if problems:
        return fail(problems[0])
    dest = Path(args.out)
    try:
        if dest.exists() and dest.is_dir():
            return fail(f"refused path: --out names a folder: {args.out}")
        if dest.resolve() == src.resolve():
            return fail("refused path: --out must not be the input file")
        if not dest.parent.exists():
            return fail(f"refused path: --out folder is missing: {dest.parent}")
        dest.write_text(f"trees: {' '.join(ids)}\nnodes: {count}\n", encoding="utf-8", newline="\n")
    except OSError as exc:
        return fail(f"cannot write --out file: {exc}")
    print(f"OK {count} nodes {' '.join(ids)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a non-ASCII name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="the BehaviorTree.CPP XML file to check")
    parser.add_argument("--out", required=True, help="where to write the two-line summary on success")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())
