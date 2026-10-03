"""Export stage: copy skill to agent target layouts. Gate: eval rate >= 0.6."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import click

TARGETS = ("claude", "codex", "opencode", "gemini")
GATE = 0.6
REPORT_FILENAME = "eval_report.json"


def load_eval_report(skilldir: Path) -> dict | None:
    """Resolve the skill's latest eval report, if one was saved beside it."""
    path = skilldir / REPORT_FILENAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _own_output_ignore(skilldir: Path, out: Path):
    """Ignore function so copytree skips our own output dir (K-07).

    When --out lives inside the skill dir (e.g. skills/<name>/export),
    a plain copytree recurses into its own destination and produces
    export/<target>/<name>/export/... nesting. Skip that top dir.
    Returns None when out is outside the skill dir (nothing to skip).
    """
    try:
        rel = out.resolve().relative_to(skilldir.resolve())
    except ValueError:
        return None
    top = rel.parts[0] if rel.parts else None
    if not top or top == ".":
        return None

    def _ignore(src: str, names: list[str]) -> list[str]:
        if Path(src).resolve() == skilldir.resolve():
            return [n for n in names if n == top]
        return []

    return _ignore


def skill_version(skilldir: Path) -> str:
    """Version from SKILL.md frontmatter (K-18); default 0.1.0 when missing."""
    try:
        text = (skilldir / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return "0.1.0"
    if not text.startswith("---"):
        return "0.1.0"
    head = text.split("---", 2)[1] if text.count("---") >= 2 else ""
    m = re.search(r"^version:\s*(\S+)", head, re.M)
    return m.group(1) if m else "0.1.0"


def export(skilldir: Path, target: str, out: Path, eval_report: dict | None = None) -> dict:
    if target not in TARGETS:
        raise click.UsageError(f"unknown target {target}; legal: claude|codex|opencode|gemini")
    report = eval_report if eval_report is not None else load_eval_report(skilldir)
    if report is None:
        raise SystemExit(
            f"eval gate refused export: no eval report found for '{skilldir.name}'; "
            "run eval first (--work/--qa) and fix the skill first"
        )
    rate = float(report.get("rate", 0.0))
    if rate < GATE:
        raise SystemExit(
            f"eval gate refused export: rate {rate:.3f} below {GATE:.1f}; fix the skill first"
        )
    dest = out / target / skilldir.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skilldir, dest, ignore=_own_output_ignore(skilldir, out))
    lock = {
        "name": skilldir.name,
        "version": skill_version(skilldir),
        "eval-rate": rate,
        "target": target,
        "date": datetime.now(timezone.utc).date().isoformat(),
    }
    (dest / ".lock.json").write_text(json.dumps(lock, indent=2), encoding="utf-8")
    receipt = {"stage": "export", "target": target, "dest": str(dest)}
    print(json.dumps(receipt, indent=2))
    return receipt
