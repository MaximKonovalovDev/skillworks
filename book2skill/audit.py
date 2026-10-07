"""Audit stage: graded token-cost report per skill (K-43, STEAL-AUDIT).

Three cost numbers without a model (idea from asale-ai/anything-to-skill
src/audit.rs, Apache-2.0, read live 2026-10-03; ideas only, no code copied):
always-loaded (SKILL.md name+description), on-trigger (SKILL.md body),
on-demand (references/). Plus body budget, description, name/dir and
broken-link checks. total_tokens stays additive over sections.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

BODY_BUDGET = 2000
TOTAL_BUDGET = 14000
DESC_MIN = 40
DESC_MAX = 1024
TRIGGER_MARKERS = ("use when", "use if", "use for")

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def _tokens(chars: int) -> int:
    return max(1, chars // 4) if chars else 0


def _frontmatter(text: str) -> dict:
    """Minimal frontmatter reader with YAML block-scalar support.

    Handles folded (``>``, ``>-``) and literal (``|``, ``|-``) values such as::

        description: >-
          Use when ...

    Continuation lines are the indented lines that follow the indicator;
    folded lines join with a space, literal lines join with a newline.
    Plain single-line ``key: value`` pairs keep the old behaviour.
    """
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    out: dict = {}
    current_key: str | None = None
    folded = False
    literal = False
    buf: list[str] = []

    def _flush() -> None:
        if current_key is not None and (folded or literal):
            if folded:
                out[current_key] = " ".join(s.strip() for s in buf if s.strip())
                # Drop blank folding lines, collapse to single spaces.
                out[current_key] = re.sub(r"\s+", " ", out[current_key]).strip()
            else:
                out[current_key] = "\n".join(s.strip() for s in buf).strip()

    for raw in parts[1].splitlines():
        if raw.strip() == "" or raw.strip().startswith("#"):
            continue
        indented = raw[:1] in (" ", "\t")
        if indented and current_key is not None:
            if not (folded or literal):
                # Plain indented continuation without an indicator: fold with a space.
                out[current_key] = re.sub(r"\s+", " ", (out[current_key] + " " + raw.strip())).strip()
            else:
                buf.append(raw.strip())
            continue
        _flush()
        current_key = None
        folded = False
        literal = False
        buf = []
        m = re.match(r"^([\w-]+):\s*(.*)$", raw.strip())
        if m:
            key, val = m.group(1), m.group(2).strip()
            indicator = val.split()[0] if val.split() else ""
            if indicator in (">", ">-", ">+", "|", "|-", "|+"):
                current_key = key
                folded = indicator.startswith(">")
                literal = indicator.startswith("|")
                out[key] = ""
            else:
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                    val = val[1:-1]
                out[key] = val.strip()
                current_key = key
    _flush()
    return out


def _skill_files(skilldir: Path) -> list[Path]:
    """Canonical .md files only; export/ dupes never counted (K-26)."""
    files = []
    for path in sorted(skilldir.rglob("*.md")):
        try:
            rel = path.relative_to(skilldir)
        except ValueError:
            continue
        if "export" in rel.parts:
            continue
        if path.is_symlink():
            continue
        files.append(path)
    return files


def audit(skilldir: Path) -> dict:
    skilldir = Path(skilldir)
    rows = []
    total = 0
    for path in _skill_files(skilldir):
        chars = len(path.read_text(encoding="utf-8"))
        tokens = chars // 4 + 10
        total += tokens
        rows.append({"file": str(path.relative_to(skilldir)), "chars": chars, "tokens": tokens})

    try:
        skill_text = (skilldir / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        skill_text = ""
    fm = _frontmatter(skill_text)
    name = fm.get("name", "")
    description = fm.get("description", "")
    body = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", skill_text, count=1, flags=re.S)

    always_loaded_tokens = _tokens(len(f"{name} {description}".strip()))
    body_tokens = _tokens(len(body))
    ref_chars = 0
    refs_dir = skilldir / "references"
    if refs_dir.is_dir():
        for path in sorted(refs_dir.rglob("*.md")):
            if "export" in path.relative_to(skilldir).parts:
                continue
            if path.is_symlink():
                continue
            try:
                ref_chars += len(path.read_text(encoding="utf-8"))
            except OSError:
                continue
    references_tokens = _tokens(ref_chars)

    flags: list[str] = []
    over_budget = body_tokens > BODY_BUDGET
    if over_budget:
        flags.append(f"body over budget ({body_tokens} > {BODY_BUDGET} tokens)")
    if total > TOTAL_BUDGET:
        flags.append(f"skill over budget ({total} > {TOTAL_BUDGET} tokens)")

    desc_reasons: list[str] = []
    dlen = len(description)
    if not description:
        desc_reasons.append("description missing")
    else:
        if not (DESC_MIN <= dlen <= DESC_MAX):
            desc_reasons.append(f"description {dlen} chars, want {DESC_MIN}-{DESC_MAX}")
        if not any(m in description.lower() for m in TRIGGER_MARKERS):
            desc_reasons.append("description needs a trigger phrase like 'Use when ...'")
    if desc_reasons:
        flags.extend(f"description: {r}" for r in desc_reasons)
    description_ok = not desc_reasons

    name_reasons: list[str] = []
    if not name:
        name_reasons.append("name missing from SKILL.md frontmatter")
    else:
        if not NAME_RE.match(name):
            name_reasons.append(f"name '{name}' breaks a-z0-9- kebab")
        if name != skilldir.name:
            name_reasons.append(f"name '{name}' must match dir '{skilldir.name}'")
    if name_reasons:
        flags.extend(f"name: {r}" for r in name_reasons)
    name_ok = not name_reasons

    broken_links: list[dict] = []
    for path in _skill_files(skilldir):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for target in LINK_RE.findall(text):
            t = target.strip().split()[0] if target.strip() else ""
            t = t.split("#")[0]
            if not t or t.startswith(("http://", "https://", "mailto:", "#")):
                continue
            candidate = (path.parent / t).resolve() if not Path(t).is_absolute() else Path(t)
            try:
                inside = candidate == skilldir.resolve() or skilldir.resolve() in candidate.parents
            except OSError:
                inside = False
            if not candidate.is_file() and not (inside and False):
                # Only flag relative links that do not resolve to a file.
                broken_links.append({"file": str(path.relative_to(skilldir)), "target": target.strip()})
    if broken_links:
        flags.append(f"broken links: {len(broken_links)}")

    report = {
        "skill": str(skilldir),
        "total_tokens": total,
        "sections": rows,
        "always_loaded_tokens": always_loaded_tokens,
        "body_tokens": body_tokens,
        "references_tokens": references_tokens,
        "body_budget": BODY_BUDGET,
        "over_budget": over_budget or total > TOTAL_BUDGET,
        "description": {"chars": dlen, "ok": description_ok, "reasons": desc_reasons},
        "name_check": {"ok": name_ok, "reasons": name_reasons},
        "broken_links": broken_links,
        "flags": flags,
    }
    print(json.dumps(report, indent=2))
    return report
