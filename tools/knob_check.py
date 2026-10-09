"""Knob config gate: unknown-key/type check plus dead-knob set-vs-read scan.

Reads the knob definitions from ``.opencode/knobs.json`` (never writes it)
and cross-checks them against the ``knobValue("name")`` reads in the
loop-keeper consumer. Exit codes: 0 clean, 1 dead knobs found (gate),
2 unknown key, bad type, or unreadable input.

Donors (MIT, ported fresh in this repo style):
  - jendrikseipp/vulture (vulture/config.py: DEFAULTS table plus the
    unknown-key / wrong-type check) -- https://github.com/jendrikseipp/vulture
  - albertusreza/dead-config (dead_config/scanner.py: set-never-read and
    read-never-set Finding kinds with an exit-1 gate)
    -- https://github.com/albertusreza/dead-config
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Known knobs and the accepted Python type(s) of each knob value.
# Mirrors vulture DEFAULTS: anything defined outside this table is refused.
KNOWNS: dict[str, tuple[type, ...]] = {
    "width": (int,),
    "dispatch": (str,),
    "heavy_max": (int,),
    "helper_max_min": (int,),
    "bg_width": (int,),
    "paid_mode": (int,),
    "repeat_cap": (int,),
    "min_free_gb": (int, float),
    "fresh_ctx_k": (int,),
}

READ_RE = re.compile(r'knobValue\(\s*["\']([A-Za-z0-9_:.~-]+)["\']\s*\)')

SCAN_SUFFIXES = (".js", ".mjs", ".cjs", ".md", ".py")


@dataclass
class Finding:
    kind: str  # unknown-key | type-mismatch | set-never-read | read-never-set
    key: str
    detail: str = ""

    def __str__(self) -> str:
        return f"{self.kind} {self.key}" + (f" ({self.detail})" if self.detail else "")


def read_defined(knobs_path: Path) -> dict:
    """Load the ``knobs`` object from knobs.json (read-only)."""
    raw = json.loads(knobs_path.read_text(encoding="utf-8"))
    defined = raw.get("knobs", raw) if isinstance(raw, dict) else {}
    if not isinstance(defined, dict):
        raise ValueError(f"{knobs_path} has no knob object")
    return defined


def check_unknown_and_types(defined: dict) -> list[Finding]:
    """Vulture half: refuse unknown keys and wrongly typed values."""
    findings: list[Finding] = []
    for key in sorted(defined):
        if key not in KNOWNS:
            findings.append(Finding("unknown-key", key, "not in KNOWNS, refusing"))
            continue
        entry = defined[key]
        value = entry.get("value") if isinstance(entry, dict) else entry
        want = KNOWNS[key]
        # bool is an int subclass; true/false is never a valid knob number.
        if isinstance(value, bool) or not isinstance(value, want):
            names = "/".join(t.__name__ for t in want)
            findings.append(
                Finding("type-mismatch", key, f"value {value!r} is not {names}")
            )
    return findings


def _iter_scan_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for suffix in SCAN_SUFFIXES:
                files.extend(sorted(path.rglob(f"*{suffix}")))
    return files


def scan_reads(paths: list[Path]) -> dict[str, list[str]]:
    """Dead-config half, read side: knobValue("name") hits with file:line."""
    reads: dict[str, list[str]] = {}
    for path in _iter_scan_files(paths):
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for match in READ_RE.finditer(line):
                try:
                    shown = str(path.relative_to(ROOT))
                except ValueError:
                    shown = str(path)
                reads.setdefault(match.group(1), []).append(f"{shown}:{lineno}")
    return reads


def cross_check(defined: dict, reads: dict[str, list[str]]) -> list[Finding]:
    """Dead-config half: set-never-read plus read-never-set Findings."""
    findings: list[Finding] = []
    for key in sorted(defined):
        if key not in reads:
            findings.append(
                Finding("set-never-read", key, "defined in knobs.json, never read")
            )
    for key in sorted(reads):
        if key not in defined:
            locs = ", ".join(reads[key][:3])
            findings.append(
                Finding("read-never-set", key, f"read at {locs}, never defined")
            )
    return findings


def check(knobs_path: Path, scan_paths: list[Path]) -> tuple[list[Finding], int]:
    """Run the full gate; exit 2 on unknown/type errors, 1 on dead knobs."""
    defined = read_defined(knobs_path)
    hard = check_unknown_and_types(defined)
    dead = cross_check(defined, scan_reads(scan_paths))
    findings = hard + dead
    if hard:
        return findings, 2
    if dead:
        return findings, 1
    return findings, 0


CORPUS_DIR = ROOT / "tests" / "fixtures" / "knobs"


def run_corpus_file(knobs_path: Path) -> tuple[list[Finding], int]:
    """Corpus runner: one knob file, valid exits 0, invalid exits 2."""
    try:
        defined = read_defined(knobs_path)
    except (OSError, ValueError) as exc:
        return [Finding("unreadable", knobs_path.name, f"{knobs_path.name}:1 {exc}")], 2
    hard = check_unknown_and_types(defined)
    if hard:
        tagged = [
            Finding(f.kind, f.key, f"{knobs_path.name}:1 {f.detail}".strip())
            for f in hard
        ]
        return tagged, 2
    reads = {key: [f"{knobs_path.name}:1"] for key in defined}
    dead = cross_check(defined, reads)
    if dead:
        return dead, 1
    return [], 0


def run_corpus_dirs(valid_dir: Path, invalid_dir: Path) -> list[str]:
    """Sweep valid/*.json (expect 0) and invalid/*.json (expect 2); return errors."""
    errors: list[str] = []
    for path in sorted(valid_dir.glob("*.json")):
        _, code = run_corpus_file(path)
        if code != 0:
            errors.append(f"{path.name}: expected exit 0, got {code}")
    for path in sorted(invalid_dir.glob("*.json")):
        _, code = run_corpus_file(path)
        if code != 2:
            errors.append(f"{path.name}: expected exit 2, got {code}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Knob unknown-key and dead-knob gate.")
    parser.add_argument("--knobs", default=str(ROOT / ".opencode" / "knobs.json"))
    parser.add_argument("--scan", nargs="*", default=[str(ROOT / ".opencode")])
    args = parser.parse_args(argv)
    try:
        findings, code = check(Path(args.knobs), [Path(p) for p in args.scan])
    except (OSError, ValueError) as exc:
        print(f"knob_check: {exc}", file=sys.stderr)
        return 2
    for finding in findings:
        print(finding)
    if code == 0:
        print("knob_check: clean")
    return code


if __name__ == "__main__":
    sys.exit(main())
