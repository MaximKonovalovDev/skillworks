"""Audit stage: token-cost report per skill section (~4 chars per token)."""
from __future__ import annotations

import json
from pathlib import Path


def audit(skilldir: Path) -> dict:
    rows = []
    total = 0
    for path in sorted(skilldir.rglob("*.md")):
        chars = len(path.read_text(encoding="utf-8"))
        tokens = chars // 4 + 10
        total += tokens
        rows.append({"file": str(path.relative_to(skilldir)), "chars": chars, "tokens": tokens})
    report = {"skill": str(skilldir), "total_tokens": total, "sections": rows}
    print(json.dumps(report, indent=2))
    return report
