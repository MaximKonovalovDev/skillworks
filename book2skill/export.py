"""Export stage: copy skill to agent target layouts. Gate: eval rate >= 0.6."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

TARGETS = ("claude", "codex", "opencode", "gemini")


def export(skilldir: Path, target: str, out: Path, eval_report: dict | None = None) -> dict:
    if target not in TARGETS:
        raise ValueError(f"unknown target {target}; legal: {sorted(TARGETS)}")
    if eval_report is not None and eval_report.get("rate", 0.0) < 0.6:
        raise SystemExit("eval gate refused export: rate below 0.6; fix the skill first")
    dest = out / target / skilldir.name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skilldir, dest)
    receipt = {"stage": "export", "target": target, "dest": str(dest)}
    print(json.dumps(receipt, indent=2))
    return receipt
