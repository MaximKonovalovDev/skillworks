"""Distill stage: reading packets plus the cure-smith gate (TS-2, R1 book-to-skill).

plan: group work/chunks into reading packets of at most PACK_TOKENS tokens.
  Every packet lists its chunk locators, so the distill pass (prompts/distill-v2.md)
  can cite them and `check` can verify them.
check: the gate a distilled skill must pass before it ships. A skill passes when
  its SKILL.md body fits the 2000-token budget, no scaffold text remains, every
  rule carries a locator, it holds 10 or more tested pairs or trials, and every
  canonical .md file is plain ASCII.

A locator is a chunk reference (NNNN.txt, optionally chunks/NNNN.txt) resolving
to the work chunks (or to the skill's own references/sources.md manifest when no
work dir is given), or a tested pair: a `###` section of references/pairs.md
carrying a `prints:` line with the measured output, or a trial row in
evals/<name>_trials.jsonl. Enforcement is pool-level: uncovered rules =
rules - locators; any uncovered rule fails the skill and is named as a
missing locator.

Ideas only, no code copied: anthropics/skills skill-creator
scripts/quick_validate.py + package_skill.py (validate-then-package shape;
licence: none declared, read live 2026-10-04) and asale-ai/anything-to-skill
src/audit.rs (graded audit; Apache-2.0, read live 2026-10-04).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import audit as audit_mod
from . import build as build_mod

PROMPT_FILE = Path(__file__).resolve().parent.parent / "prompts" / "distill-v2.md"

PACK_TOKENS = 6000       # a reading packet never exceeds this (tokens as chars // 4)
BODY_BUDGET = 2000       # SKILL.md body, same estimate as audit.py
MIN_PAIRS = 10           # tested pairs or trials a distilled skill must hold

CHUNK_REF_RE = re.compile(r"`((?:chunks/)?(\d{4})\.txt)`")
PAIR_HEAD_RE = re.compile(r"(?m)^###\s+")

# A bullet that states something checkable: an actionable rule carries code.
BULLET_RE = re.compile(r"^\s*[-*]\s+.*`[^`]+`.*$")

# Signature sentence of the build scaffold body (build._scaffold_body). A skill
# whose SKILL.md grew a Sources section on top of the scaffold still carries
# scaffold text; build.scaffold_leftovers only sees exact file matches.
SCAFFOLD_SENTENCE = "Built from owned sources. Start with `chapters/notes.md`"


def _scaffold_hits(skilldir: Path, body: str) -> list[str]:
    hits = list(build_mod.scaffold_leftovers(skilldir))
    if SCAFFOLD_SENTENCE in body and "SKILL.md" not in hits:
        hits.append("SKILL.md")
    return hits


def _ascii_escape(chars: str) -> str:
    """U+XXXX escapes so a finding prints on any console (never raw non-ASCII)."""
    return " ".join(f"U+{ord(c):04X}" for c in chars)


_PROMPT_CACHE = None


def prompt_version() -> str:
    global _PROMPT_CACHE
    if _PROMPT_CACHE is not None:
        return _PROMPT_CACHE
    """Version stamp of the distill prompt fragment (llm pattern, like build.py)."""
    try:
        text = PROMPT_FILE.read_text(encoding="utf-8")
    except OSError:
        return "inline"
    m = re.search(r"^version:\s*(\S+)", text, re.M)
    _PROMPT_CACHE = m.group(1) if m else "unversioned"
    return _PROMPT_CACHE


def _tokens(chars: int) -> int:
    return chars // 4


def plan(workdir: Path, packet_tokens: int = PACK_TOKENS) -> dict:
    """Group work/chunks into reading packets of at most packet_tokens tokens.

    Writes work/distill_plan.json (packet id, chunk locators, chars, tokens)
    and returns the receipt. A single oversized chunk keeps its own packet.
    """
    workdir = Path(workdir)
    chunk_files = sorted((workdir / "chunks").glob("*.txt"))
    if not chunk_files:
        raise ValueError(f"distill plan: no chunks in {workdir / 'chunks'}; run split first")
    packets: list[dict] = []
    cur: list[Path] = []
    cur_chars = 0

    def flush() -> None:
        toks = _tokens(cur_chars)
        packets.append({
            "id": f"packet-{len(packets):02d}",
            "chunks": [p.name for p in cur],
            "chars": cur_chars,
            "tokens": toks,
        })

    for path in chunk_files:
        n = path.stat().st_size  # bytes~=chars; no big-file read
        if cur and _tokens(cur_chars + n) > packet_tokens:
            flush()
            cur, cur_chars = [], 0
        cur.append(path)
        cur_chars += n
    if cur:
        flush()
    total_tokens = sum(p["tokens"] for p in packets)
    receipt = {
        "stage": "distill-plan",
        "work": str(workdir),
        "prompt": prompt_version(),
        "packet_tokens": packet_tokens,
        "packets": packets,
        "chunks": len(chunk_files),
        "total_tokens": total_tokens,
    }
    (workdir / "distill_plan.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(f"distill plan: {len(packets)} packets over {len(chunk_files)} chunks, "
          f"{total_tokens} tokens (cap {packet_tokens}/packet)")
    for p in packets:
        print(f"  {p['id']}: {len(p['chunks'])} chunks, {p['tokens']} tokens "
              f"({p['chunks'][0]}..{p['chunks'][-1]})")
    return receipt


def _body(skilldir: Path) -> str:
    text = (skilldir / "SKILL.md").read_text(encoding="utf-8")
    return re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)


def _rules(body: str) -> list[str]:
    return [ln for ln in body.splitlines() if BULLET_RE.match(ln)]


def _pairs_with_prints(skilldir: Path) -> tuple[int, int]:
    """(pair sections, sections carrying a prints: line) in references/pairs.md."""
    pairs = skilldir / "references" / "pairs.md"
    if not pairs.is_file():
        return 0, 0
    text = pairs.read_text(encoding="utf-8")
    sections = [s for s in PAIR_HEAD_RE.split(text)[1:] if s.strip()]
    with_prints = sum(1 for s in sections if "prints:" in s)
    return len(sections), with_prints


def _trials(skilldir: Path, root: Path) -> int:
    trials = root / "evals" / f"{skilldir.name}_trials.jsonl"
    if not trials.is_file():
        return 0
    count = 0
    with trials.open(encoding="utf-8") as fh:
        for ln in fh:
            if ln.strip():
                count += 1
    return count


def _chunk_refs_ok(body: str, skilldir: Path, workdir: Path | None) -> tuple[int, list[str]]:
    """Chunk locators in the SKILL.md body that resolve; dangling ones listed."""
    refs = CHUNK_REF_RE.findall(body)
    ok = 0
    dangling: list[str] = []
    manifest = ""
    sources = skilldir / "references" / "sources.md"
    if sources.is_file():
        manifest = sources.read_text(encoding="utf-8")
    for full, _num in refs:
        base = full.split("/")[-1]
        if workdir is not None and (workdir / "chunks" / base).is_file():
            ok += 1
        elif f"`{base}`" in manifest or full in manifest:
            ok += 1
        else:
            dangling.append(full)
    return ok, dangling


def _ascii_findings(skilldir: Path) -> list[str]:
    # Non-ASCII carriers per skill file.
    found: list[str] = []
    for path in audit_mod._skill_files(skilldir):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        bad = sorted({c for c in text if ord(c) > 126})
        if bad:
            found.append(f"{path.relative_to(skilldir)}: {_ascii_escape(''.join(bad[:5]))}")
    return found


def check(skilldir: Path, workdir: Path | None = None) -> dict:
    """Run the distill gate over a skill. Returns the report; ok=False on any finding."""
    skilldir = Path(skilldir)
    root = Path(__file__).resolve().parent.parent  # repo root, like gates.py
    findings: list[str] = []
    if not (skilldir / "SKILL.md").is_file():
        return {
            "skill": str(skilldir), "ok": False,
            "findings": ["SKILL.md missing"],
        }
    body = _body(skilldir)
    body_tokens = len(body) // 4 + 10
    if body_tokens > BODY_BUDGET:
        findings.append(f"body over budget ({body_tokens} > {BODY_BUDGET} tokens)")

    leftovers = _scaffold_hits(skilldir, body)
    if leftovers:
        findings.append(f"scaffold text remains in: {', '.join(leftovers)}")

    rules = _rules(body)
    chunk_ok, dangling = _chunk_refs_ok(body, skilldir, Path(workdir) if workdir else None)
    pair_sections, pairs_prints = _pairs_with_prints(skilldir)
    trials = _trials(skilldir, root)
    locators = chunk_ok + pairs_prints + trials
    uncovered = max(0, len(rules) - locators)
    if dangling:
        findings.append(f"missing locators (dangling chunk refs: {', '.join(sorted(set(dangling)))})")
    if uncovered:
        findings.append(
            f"missing locators: {uncovered} of {len(rules)} rules carry no locator "
            f"({locators} locators: {chunk_ok} chunk refs, {pairs_prints} tested pairs, {trials} trials)"
        )

    pairs_total = pair_sections + trials
    if pairs_total < MIN_PAIRS:
        findings.append(f"only {pairs_total} tested pairs or trials, need {MIN_PAIRS} or more")

    ascii_bad = _ascii_findings(skilldir)
    if ascii_bad:
        findings.append(f"non-ASCII characters in: {'; '.join(ascii_bad)}")

    report = {
        "skill": str(skilldir),
        "work": str(workdir) if workdir else None,
        "prompt": prompt_version(),
        "body_tokens": body_tokens,
        "body_budget": BODY_BUDGET,
        "rules": len(rules),
        "locators": {"chunk_refs": chunk_ok, "tested_pairs": pairs_prints, "trials": trials},
        "uncovered_rules": uncovered,
        "pairs_total": pairs_total,
        "pairs_minimum": MIN_PAIRS,
        "scaffold_leftovers": leftovers,
        "ascii_bad": ascii_bad,
        "findings": findings,
        "ok": not findings,
    }
    print(json.dumps(report, indent=2))
    return report
