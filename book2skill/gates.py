"""Shared gates for the fleet skills (skills the other repos' loops load).

A fleet skill is written from a licensed manual to fix a measured mistake the
loops make. These gates keep the format honest; each skill's own test file
adds the executable checks (the examples in the skill really run).

Single code path (TS-2): this module owns the implementation.
``tests/skill_gates.py`` is a thin re-export shim so existing imports
(``test_fleet_skills.py``, ``live_proof.py``) keep working.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import warnings
from pathlib import Path

import pytest

from . import audit as audit_mod
from . import eval as eval_mod
from . import index as index_mod
from . import split as split_mod

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

__all__ = [
    "ROOT", "SKILLS", "FLEET_SKILLS", "FORGE_SAFE", "LIVE", "live",
    "PROOF_NAME", "BODY_TOKEN_BUDGET", "TOTAL_TOKEN_BUDGET", "QA_MIN",
    "EVAL_GATE", "LICENSES", "JARGON",
    "frontmatter", "body_of", "body_tokens", "skill_files", "skill_text",
    "forge_english_hits", "check_format", "check_sources", "check_eval",
    "test_file_for", "fingerprint", "check_proof",
]

# name -> substrings THIRD_PARTY_NOTICES.md must carry for it (an empty list: original work, no outside source to credit)
FLEET_SKILLS = {
    "pwsh-for-bash-writers": ["MicrosoftDocs/PowerShell-Docs"],
    "git-one-branch": ["progit/progit2"],
    "real-browser-automation": ["microsoft/playwright", "devtools-protocol"],
    "bevy-rust-ecs": ["bevyengine/bevy"],
    "cron-skip-clean": [],
    "pipe-run": [],
    "inbox-file-reader": [],
    "book-to-skill": [],
    "engine-builder": ["engine-builder (MIT"],
    "repo-read-first": ["cli/cli (MIT"],
    "edit-reread": ["PowerShell-Docs"],
    "edit-unique": [],
    "task-scope": [],
    "bash-abort-guard": [],
    "ready-file-check": [],
    "bash-allowlist": [],
    "task-abort-guard": [],
    "bash-spawn-guard": [],
    "read-offset-guard": [],
    "cargo-book": ["rust-lang/cargo"],
    "fetch-github-first": ["cli/cli (MIT)"],
    "playwright-docs": ["microsoft/playwright"],
    "edit-verify": ["cline/cline", "aider-ai/aider", "sst/opencode"],
    "websearch-retry": [],
    "repomap-guard": [],
    "edit-identical": [],
    "keeper-ready": [],
    "read-abort-guard": [],
    "edit-abort-guard": [],
    "ripgrep-search": ["BurntSushi/ripgrep"],
    "axios-get": ["axios/axios"],
    "octokit-request": ["octokit/request"],
    "repro-first": [],
    "judge-score-risk": [],
    "batch-first": [],
    "brief-gate": [],
}
# Installed in forge, whose `node scripts/check.mjs` bans some English words.
FORGE_SAFE = {"pwsh-for-bash-writers", "git-one-branch", "cron-skip-clean", "pipe-run", "inbox-file-reader"}

# Live tests run real programs (pwsh, git, a browser) and are slow; the loops' shell kills a command at 120 s.
# They run when SKILL_LIVE=1. `python tests/live_proof.py` runs them and records a fingerprint of the skill;
# the default run only checks that the skill still matches its last live proof.
LIVE = os.environ.get("SKILL_LIVE") == "1"
live = pytest.mark.skipif(not LIVE, reason="live test: set SKILL_LIVE=1 (python tests/live_proof.py runs them all)")
if not LIVE:
    warnings.warn(
        "live tests skipped: set SKILL_LIVE=1 to run them (python tests/live_proof.py runs them all)",
        UserWarning,
        stacklevel=2,
    )
PROOF_NAME = "live-proof.json"
NUL, CRLF, LF = bytes([0]), bytes([13, 10]), bytes([10])

BODY_TOKEN_BUDGET = 2000     # SKILL.md body, tokens as audit.py counts them
TOTAL_TOKEN_BUDGET = 14000   # every canonical .md of the skill
QA_MIN = 8
EVAL_GATE = 0.9              # the export gate is 0.6; fleet skills are stricter

LICENSES = ("CC-BY-4.0", "MIT", "Apache-2.0", "BSD-3-Clause", "CC-BY-NC-SA-3.0")

JARGON = ("ponytail astra pony splay f10x horse horses door doors hatch hatches receipt receipts "
          "ratchet ratchets face slot slots wave waves ride arm burst lane lanes").split()
JARGON_RE = re.compile(r"\b(" + "|".join(JARGON) + r")\b", re.I)
WAVE_RE = re.compile(r"\b(?:[WF]\d{1,2}|[Ww]ave\s*-?\s*\d+|w-[a-z0-9]+(?:-[a-z0-9]+)*|w\d+[a-z0-9]*(?:-[a-z0-9]+)*)\b")


def frontmatter(text: str) -> dict[str, str]:
    """Frontmatter reader with YAML block-scalar folding (same as audit._frontmatter).

    Folded (``>``, ``>-``) continuations join with a space, literal
    (``|``, ``|-``) continuations join with a newline; plain
    ``key: value`` pairs keep the old behaviour.
    """
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not m:
        return {}
    out: dict[str, str] = {}
    current_key: str | None = None
    folded = False
    literal = False
    buf: list[str] = []

    def _flush() -> None:
        if current_key is not None and (folded or literal):
            if folded:
                joined = " ".join(s.strip() for s in buf if s.strip())
                out[current_key] = re.sub(r"\s+", " ", joined).strip()
            else:
                out[current_key] = "\n".join(s.strip() for s in buf).strip()

    for line in m.group(1).splitlines():
        if line.strip() == "" or line.strip().startswith("#"):
            continue
        indented = line[:1] in (" ", "\t")
        if indented and current_key is not None:
            if not (folded or literal):
                out[current_key] = re.sub(r"\s+", " ", (out[current_key] + " " + line.strip())).strip()
            else:
                buf.append(line.strip())
            continue
        _flush()
        current_key = None
        folded = False
        literal = False
        buf = []
        kv = re.match(r"^([\w-]+):\s*(.*)$", line.strip())
        if kv:
            key, val = kv.group(1), kv.group(2).strip()
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


def body_of(text: str) -> str:
    return re.sub(r"^---\r?\n.*?\r?\n---\r?\n", "", text, count=1, flags=re.S)


def body_tokens(text: str) -> int:
    return len(body_of(text)) // 4 + 10  # same estimate as book2skill/audit.py


def skill_files(name: str) -> list[Path]:
    return sorted(p for p in (SKILLS / name).rglob("*.md") if "export" not in p.relative_to(SKILLS / name).parts)


def skill_text(name: str) -> str:
    return "\n\n".join(p.read_text(encoding="utf-8") for p in skill_files(name))


def _strip_code_spans(line: str) -> str:
    """Mirror forge scripts/check.mjs stripCodeSpans: spans standing apart from words are blanked."""
    def paired(m: re.Match[str]) -> str:
        before = line[m.start() - 1] if m.start() > 0 else ""
        after = line[m.end()] if m.end() < len(line) else ""
        if re.match(r"[A-Za-z0-9]", before) or re.match(r"[A-Za-z0-9]", after):
            return m.group(0)[1:-1]
        return " " * len(m.group(0))
    return re.sub(r"`+", " ", re.sub(r"`[^`]*`", paired, line))


def forge_english_hits(name: str) -> list[str]:
    hits = []
    for path in skill_files(name):
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for m in JARGON_RE.finditer(_strip_code_spans(line)):
                hits.append(f"{path.relative_to(SKILLS)}:{n} jargon {m.group(1)}")
            w = WAVE_RE.search(line)
            if w:
                hits.append(f"{path.relative_to(SKILLS)}:{n} wave-id {w.group(0)}")
    return hits


def check_format(name: str) -> None:
    d = SKILLS / name
    md = d / "SKILL.md"
    assert md.is_file(), f"{name}: SKILL.md missing"
    text = md.read_text(encoding="utf-8")
    fm = frontmatter(text)
    assert fm.get("name") == name, f"{name}: frontmatter name {fm.get('name')!r} must equal the folder"
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) and len(name) <= 64
    desc = fm.get("description", "")
    assert 40 <= len(desc) <= 1024, f"{name}: description is {len(desc)} chars, want 40-1024"
    assert re.search(r"\bUse (when|before|whenever|for)\b", desc), f"{name}: description needs a 'Use when/before/whenever' trigger"
    assert fm.get("license"), f"{name}: license line missing"
    assert body_tokens(text) <= BODY_TOKEN_BUDGET, f"{name}: SKILL.md body is {body_tokens(text)} tokens, budget {BODY_TOKEN_BUDGET}"
    # every referenced file must exist
    for rel in set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", text)):
        assert (d / rel).exists(), f"{name}: SKILL.md names {rel} but it does not exist"
    # plain ASCII so no tool output turns into mojibake on this Windows PC
    for p in skill_files(name):
        bad = [c for c in p.read_text(encoding="utf-8") if ord(c) > 126]
        assert not bad, f"{name}: {p.name} has non-ASCII characters {sorted(set(bad))[:5]}"
    report = audit_mod.audit(d)
    assert report["total_tokens"] <= TOTAL_TOKEN_BUDGET, f"{name}: skill is {report['total_tokens']} tokens, budget {TOTAL_TOKEN_BUDGET}"
    if name in FORGE_SAFE:
        hits = forge_english_hits(name)
        assert not hits, f"{name}: words forge's English check bans: {hits[:6]}"


def check_sources(name: str) -> None:
    src = SKILLS / name / "references" / "sources.md"
    assert src.is_file(), f"{name}: references/sources.md missing"
    text = src.read_text(encoding="utf-8")
    assert "https://" in text and "verified" in text.lower(), f"{name}: sources.md needs URLs and a 'verified' date"
    assert any(lic in text for lic in LICENSES), f"{name}: sources.md must state a licence"
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for needle in FLEET_SKILLS[name]:
        assert needle in notices, f"THIRD_PARTY_NOTICES.md must credit {needle}"


def check_eval(name: str) -> float:
    """The pipeline's own eval over the skill's text: can a question the loops really ask be answered from it?"""
    qa = ROOT / "evals" / f"{name}_qa.jsonl"
    assert qa.is_file(), f"{name}: evals/{name}_qa.jsonl missing"
    rows = [json.loads(line) for line in qa.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(rows) >= QA_MIN, f"{name}: {len(rows)} QA rows, want {QA_MIN}+"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "work"
        work.mkdir()
        (work / "full_text.txt").write_text(skill_text(name), encoding="utf-8")
        split_mod.split(work, chunk=1500, overlap=100)
        index_mod.build_index(work)
        report = eval_mod.run_eval(work, Path(tmp) / "skill", qa)
    assert report["rate"] >= EVAL_GATE, f"{name}: eval rate {report['rate']:.3f} below {EVAL_GATE}"
    return report["rate"]


def test_file_for(name: str) -> Path:
    return ROOT / "tests" / f"test_{name.replace('-', '_')}.py"


def fingerprint(name: str) -> str:
    """sha256 over the skill folder (except the proofs themselves), its QA file and its test file."""
    d = SKILLS / name
    h = hashlib.sha256()
    files = [p for p in sorted(d.rglob("*")) if p.is_file() and p.name not in (PROOF_NAME, "trial-proof.json", "eval_report.json")
             and "export" not in p.relative_to(d).parts and "__pycache__" not in p.parts]
    files += [ROOT / "evals" / f"{name}_qa.jsonl", test_file_for(name)]
    for p in files:
        if not p.is_file():
            continue
        rel = p.relative_to(ROOT).as_posix()
        h.update(rel.encode() + NUL + p.read_bytes().replace(CRLF, LF) + NUL)
    return h.hexdigest()


def check_proof(name: str) -> dict:
    """The skill must match the fingerprint recorded when its live tests last passed."""
    proof = SKILLS / name / "references" / PROOF_NAME
    assert proof.is_file(), f"{name}: no live proof yet. Run: python tests/live_proof.py {name}"
    data = json.loads(proof.read_text(encoding="utf-8"))
    assert data.get("fingerprint") == fingerprint(name), (
        f"{name}: changed since its live tests last passed ({data.get('date')}). Run: python tests/live_proof.py {name}")
    return data
