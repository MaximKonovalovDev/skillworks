"""Edit guard: refuse a stale oldString before an edit (DRY-EDIT, R4 packs beyond wrappers).

    python tools/edit_guard.py --file <target> [--old-file <old-text>] [--old-string "..."]
    echo <old-text> | python tools/edit_guard.py --file <target>
    python tools/edit_guard.py --help

Given a file path and a literal oldString (via --old-file or stdin), exit 0
with EDIT GUARD PASS when the string is present exactly; else exit 1 quoting
the rule and printing the closest matching lines with their exact whitespace
(tabs shown as \\t, carriage returns as \\r) so the caller re-reads precisely.
Reads the target with newlines preserved, so a CRLF file versus an LF
oldString is diagnosed, not silently passed. Writes nothing.
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

RULE = "re-read the file before editing; the edit tool needs the exact text"
REFUSAL = f"edit_guard: refused: oldString not found ({RULE})"


def read_preserved(path: Path) -> str:
    with open(path, "r", encoding="utf-8", newline="") as fh:
        return fh.read()


def ending_style(text: str) -> str:
    crlf = text.count("\r\n")
    lf = text.count("\n") - crlf
    lone_cr = text.count("\r") - crlf
    if crlf and not lf and not lone_cr:
        return "CRLF"
    if lf and not crlf and not lone_cr:
        return "LF"
    if not text:
        return "empty"
    return f"mixed(CRLF={crlf},LF={lf},CR={lone_cr})"


def visible(line: str) -> str:
    return line.replace("\t", "\\t").replace("\r", "\\r")


def closest(target_lines: list[str], want: str, top: int = 3) -> list[tuple[int, float, str]]:
    scored: list[tuple[int, float, str]] = []
    for i, have in enumerate(target_lines, start=1):
        ratio = difflib.SequenceMatcher(None, want, have.strip("\r\n")).ratio()
        scored.append((i, ratio, have))
    scored.sort(key=lambda t: t[1], reverse=True)
    return scored[:top]


def diagnose(target_path: str, text: str, old: str) -> list[str]:
    lines: list[str] = []
    lines.append(REFUSAL + f" in {target_path}")
    t_lines = text.splitlines(keepends=True)
    o_lines = old.splitlines(keepends=True)
    t_disp = text.splitlines()
    lines.append(
        f"file: {len(t_disp)} lines, endings {ending_style(text)}, "
        f"tabs {text.count(chr(9))}, lines with trailing spaces "
        f"{sum(1 for ln in t_disp if ln != ln.rstrip(' '))}"
    )
    lines.append(
        f"old: {len(old.splitlines())} lines, endings {ending_style(old)}, "
        f"tabs {old.count(chr(9))}"
    )
    if ending_style(text) == "CRLF" and "\r" not in old:
        lines.append("hint: file is CRLF but oldString has no \\r (read the file raw; copy the exact bytes)")
    if text.count("\t") and "\t" not in old and "    " in old:
        lines.append("hint: file uses tabs but oldString uses spaces (tabs shown as \\t below)")
    if "    " in text and "\t" in old and "\t" not in text:
        lines.append("hint: file uses spaces but oldString uses tabs (tabs shown as \\t below)")
    shown = 0
    for want in old.splitlines()[:5]:
        if not want.strip():
            continue
        for num, ratio, have in closest(t_disp, want):
            raw = have.rstrip("\n")
            lines.append(f"closest line {num} ({ratio:.2f}): {visible(raw)}")
            shown += 1
            if shown >= 3:
                break
        if shown >= 3:
            break
    if shown == 0 and t_disp:
        for num in (1, len(t_disp) // 2 + 1, len(t_disp)):
            if 1 <= num <= len(t_disp):
                lines.append(f"closest line {num} (0.00): {visible(t_disp[num - 1].rstrip(chr(10)))}")
    lines.append(f"rule: {RULE}")
    return lines


def check_file(target: Path, old: str) -> tuple[int, list[str]]:
    try:
        text = read_preserved(target)
    except OSError:
        return 1, [f"edit_guard: refused: cannot read {target} (check the path and {RULE})"]
    if not old:
        return 1, [f"edit_guard: refused: empty oldString ({RULE})"]
    if old in text:
        count = text.count(old)
        style = ending_style(text)
        return 0, [f"EDIT GUARD PASS file {target} lines {len(text.splitlines())} endings {style} matches {count}"]
    return 1, diagnose(str(target), text, old)


def read_old(args: argparse.Namespace) -> str:
    if args.old_string is not None:
        return args.old_string
    if args.old_file is not None:
        return read_preserved(Path(args.old_file))
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--file", default=None, help="target file to check the oldString against")
    ap.add_argument("positional_file", nargs="?", default=None, help="target file (when --file is absent)")
    ap.add_argument("positional_old", nargs="?", default=None, help="file holding the literal oldString (else stdin)")
    ap.add_argument("--old-file", default=None, help="file holding the literal oldString")
    ap.add_argument("--old-string", default=None, help="literal oldString on the command line")
    args = ap.parse_args(argv)
    target_name = args.file or args.positional_file
    if target_name is None:
        print(f"edit_guard: refused: no file given ({RULE})")
        return 2
    old_path = args.old_file or args.positional_old
    if args.old_string is not None:
        old = args.old_string
    elif old_path is not None:
        try:
            old = read_preserved(Path(old_path))
        except OSError:
            print(f"edit_guard: refused: cannot read oldString file {old_path} ({RULE})")
            return 1
    else:
        old = read_old(args)
    rc, lines = check_file(Path(target_name), old)
    for ln in lines:
        print(ln)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
