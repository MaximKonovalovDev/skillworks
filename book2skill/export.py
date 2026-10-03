"""Export stage: copy skill to agent target layouts. Gate: eval rate >= 0.6."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

TARGETS = ("claude", "codex", "opencode", "gemini")
GATE = 0.6
REPORT_FILENAME = "eval_report.json"


def load_eval_report(skilldir: Path) -> dict | None:
    """Resolve the skill's latest eval report, if one was saved beside it."""
    path = skilldir / REPORT_FILENAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def export(skilldir: Path, target: str, out: Path, eval_report: dict | None = None) -> dict:
    if target not in TARGETS:
        raise ValueError(f"unknown target {target}; legal: {sorted(TARGETS)}")
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
    shutil.copytree(skilldir, dest)
    receipt = {"stage": "export", "target": target, "dest": str(dest)}
    print(json.dumps(receipt, indent=2))
    return receipt
