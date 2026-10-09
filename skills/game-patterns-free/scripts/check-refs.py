#!/usr/bin/env python3
"""check-refs: verify game-patterns-free domain split holds.

Checks that patterns.md is the index, SKILL.md loads patterns plus
ONE domain only, the 4 domain refs exist and hold their markers,
and no stale chapters/notes.md load remains.

Usage:
    python scripts/check-refs.py [--skill DIR]

Exit 0 on PASS, 1 on FAIL. First word of stdout is PASS or FAIL.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DOMAINS = ("sequencing", "decoupling", "optimization", "behavioral")
DOMAIN_PATTERNS = {
    "sequencing": ["processInput", "MS_PER_FRAME", "Skeleton", "wasSlapped"],
    "decoupling": ["Bjorn", "InputComponent", "onNotify", "pending_", "singleton"],
    "optimization": ["ParticlePool", "CELL_SIZE", "GraphNode", "NUM_THINGS"],
    "behavioral": ["interpret", "bytecode", "Heroine", "Superpower", "Breed"],
}
NEEDLES_NOTES = ("code/cpp", "MIT", "Bjorn", "InputComponent", "interpret", "bytecode")


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def check(skill: Path) -> list[str]:
    errors: list[str] = []
    refs = skill / "references"
    for d in DOMAINS:
        p = refs / (d + ".md")
        if not p.is_file():
            fail("missing references/" + d + ".md", errors)
            continue
        t = p.read_text(encoding="utf-8")
        for n in ("code/cpp", "MIT", "NonCommercial", "never sold", "Contents", "Sample Code"):
            if n not in t:
                fail("references/" + d + ".md lacks " + repr(n), errors)
        for n in DOMAIN_PATTERNS[d]:
            if n not in t:
                fail("references/" + d + ".md lacks marker " + repr(n), errors)
        if "game-programming-patterns" not in t:
            fail("references/" + d + ".md lacks source repo", errors)
    pat = skill / "patterns.md"
    if not pat.is_file():
        fail("missing patterns.md", errors)
    else:
        t = pat.read_text(encoding="utf-8")
        if "Section map:" not in t:
            fail("patterns.md lacks Section map", errors)
        for d in DOMAINS:
            if "references/" + d + ".md" not in t:
                fail("patterns.md lacks pointer references/" + d + ".md", errors)
        for n in ("MIT code", "game-programming-patterns", "Sequencing Patterns", "Game Loop"):
            if n not in t:
                fail("patterns.md lacks " + repr(n), errors)
    sk = skill / "SKILL.md"
    if not sk.is_file():
        fail("missing SKILL.md", errors)
    else:
        t = sk.read_text(encoding="utf-8")
        if "patterns.md" not in t:
            fail("SKILL.md must load patterns.md", errors)
        if "chapters/notes.md" in t:
            fail("SKILL.md must not load chapters/notes.md", errors)
        low = t.lower()
        if "only the one" not in low and "one domain" not in low and "only one" not in low:
            fail("SKILL.md must say read only ONE domain", errors)
        if "scripts/check-refs.py" not in t:
            fail("SKILL.md must name scripts/check-refs.py", errors)
    notes = skill / "chapters" / "notes.md"
    if not notes.is_file():
        fail("missing chapters/notes.md pointer", errors)
    else:
        t = notes.read_text(encoding="utf-8")
        if "moved" not in t.lower() or "patterns.md" not in t:
            fail("chapters/notes.md must be a pointer to patterns.md", errors)
        for n in NEEDLES_NOTES:
            if n not in t:
                fail("chapters/notes.md pointer lacks " + repr(n), errors)
    for p in sorted(skill.rglob("*")):
        if not p.is_file():
            continue
        try:
            rel = p.relative_to(skill)
        except ValueError:
            continue
        if "export" in rel.parts or "__pycache__" in p.parts:
            continue
        if p.suffix not in (".md", ".py", ".json", ".jsonl"):
            continue
        if p.name in ("live-proof.json", "trial-proof.json", "eval_report.json"):
            continue
        try:
            t = p.read_text(encoding="utf-8")
        except OSError as exc:
            fail("cannot read " + str(rel) + ": " + str(exc), errors)
            continue
        bad = sorted({c for c in t if ord(c) > 126})
        if bad:
            fail(str(rel) + " has non-ASCII " + repr(bad[:3]), errors)
        priv = "User" + "s"
        has_win = (priv in t and ":\\" in t)
        has_nix = ("/" + priv + "/" in t)
        has_tok = ("gh" + "p_" in t) or (("github" + "_pat_") in t)
        if has_win or has_nix or has_tok:
            fail(str(rel) + " carries a private path or secret", errors)
    qa = Path(__file__).resolve().parents[2].parents[0] / "evals" / "game-patterns-free_qa.jsonl"
    alt = skill.parents[1] / "evals" / "game-patterns-free_qa.jsonl"
    qapath = qa if qa.is_file() else alt
    if qapath.is_file():
        texts = []
        for p in sorted(skill.rglob("*.md")):
            try:
                rel = p.relative_to(skill)
            except ValueError:
                continue
            if "export" in rel.parts:
                continue
            texts.append(p.read_text(encoding="utf-8").lower())
        blob = "\n\n".join(texts)
        for line in qapath.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            for m in row.get("must", []):
                if m.lower() not in blob:
                    fail("QA must " + repr(m) + " missing from skill text", errors)
    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify game-patterns-free refs hold.")
    ap.add_argument("--skill", default=None, help="skill dir (default: parent of scripts/)")
    args = ap.parse_args(argv)
    skill = Path(args.skill) if args.skill else Path(__file__).resolve().parents[1]
    errors = check(skill)
    if errors:
        print("FAIL " + str(len(errors)) + " problems")
        for e in errors[:20]:
            print("- " + e)
        return 1
    print("PASS 4 domains, patterns index ok, SKILL router ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
