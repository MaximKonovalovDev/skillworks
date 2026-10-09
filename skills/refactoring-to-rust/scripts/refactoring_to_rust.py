#!/usr/bin/env python3
"""refactoring-to-rust: a fleet skill script.

Headless: no network, no prompts. Reads a snippet list and writes a pattern report.

Usage:
    python scripts/refactoring_to_rust.py --input <path> --out <path>

The first word of stdout is the answer. Exit codes: 0 when the work is done, 2 on bad input.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DESCRIPTION = "Other-language to Rust port patterns for stealing game code into Rust. Use when porting C, Python or JS game code to Rust or stealing Bevy methods into our renderer."

RULES = (
    ("C-STRING", ("cstring", "cstr", "char*")),
    ("FFI-BOUNDARY", ("extern", "ffi", "unsafe")),
    ("PYCLASS-STRUCT", ("pyclass", "pymethods", "pyo3", "class")),
    ("RESULT-ERROR", ("except", "raise", "result", "throws", "catch")),
    ("WASM-ASYNC", ("promise", "async", "await", "wasm-bindgen")),
    ("SERDE-JSON", ("json", "serde", "from_str")),
    ("WASM-BUILD", ("wasm-pack", "cargo install", "pkg")),
    ("TRAIT-IMPL", ("inherit", "trait", "impl", "virtual")),
    ("OWNERSHIP-MOVE", ("malloc", "free(", "clone()", "box<", "move")),
)


def classify(snippet: str) -> str:
    lowered = snippet.lower()
    for tag, keys in RULES:
        for key in keys:
            if key in lowered:
                return tag
    return "OTHER"


def work(args: argparse.Namespace) -> int:
    in_path = Path(args.input)
    out_path = Path(args.out)
    if not in_path.is_file():
        print("ERROR missing input " + str(args.input))
        return 2
    try:
        text = in_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print("ERROR input is not utf-8 text " + str(args.input))
        return 2
    snippets = [line.strip() for line in text.splitlines() if line.strip()]
    if not snippets:
        print("ERROR empty input " + str(args.input))
        return 2
    tagged = [(classify(snippet), snippet) for snippet in snippets]
    distinct = len({tag for tag, _snippet in tagged})
    if out_path.parent.as_posix() not in ("", "."):
        out_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# refactoring-to-rust report: "
        + str(len(tagged))
        + " snippets, "
        + str(distinct)
        + " patterns"
    ]
    for number, (tag, snippet) in enumerate(tagged, 1):
        lines.append(str(number).zfill(2) + ": " + tag + " <= " + snippet[:160])
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        "PORTED "
        + str(distinct)
        + " patterns from "
        + str(len(tagged))
        + " snippets to "
        + str(args.out)
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # a non-ASCII name must not crash a pipe set to a legacy code page
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument("--input", required=True, help="snippet list file, one snippet per line")
    parser.add_argument("--out", required=True, help="report file to write")
    args = parser.parse_args(argv)
    return work(args)


if __name__ == "__main__":
    raise SystemExit(main())

