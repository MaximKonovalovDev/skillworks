"""Minimal stdio MCP server: skill_search + skill_preview over built skills.

Speaks JSON-RPC over stdio with initialize / tools/list / tools/call.
Tools: skill_search {query, skill?} — substring rank over skill markdown;
  skill_preview {skill} — README-then-SKILL.md fallback head for inspect-before-install.
No dependencies, no network. Scope is honest: search + preview only, no generation.
"""
from __future__ import annotations

import argparse
import hashlib
import inspect
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

SKILLS_DIR_ENV_VARS = ("SKILLWORKS_SKILLS_DIR", "SKILLS_DIR")

_CLI_SKILLS_DIR: Path | None = None


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Minimal stdio MCP server: skill_search + skill_preview over built skills. Speaks JSON-RPC over stdio with initialize / tools/list / tools/call. Tools: skill_search (the list entry -- use a broad query to browse) and skill_preview (README-then-SKILL.md head for inspect-before-install).",
        epilog="Reads JSON-RPC requests on stdin, writes replies on stdout. Example: python mcp_server/server.py --skills-dir ./skills",
    )
    parser.add_argument("--skills-dir", default=None, help="Skills directory to serve (default: ./skills; overrides SKILLWORKS_SKILLS_DIR/SKILLS_DIR).")
    return parser


def _skills_dir() -> Path:
    if _CLI_SKILLS_DIR is not None:
        return _CLI_SKILLS_DIR
    for var in SKILLS_DIR_ENV_VARS:
        val = os.environ.get(var)
        if val:
            return Path(val)
    return SKILLS

CACHE_HINT = {"ttlMs": 3600000, "scope": "public"}

EVAL_GATE = 0.6

# Attested trust tier -- steal from roli-lpci/sigistry-marketplace@a7a30de (licence MIT,
# https://github.com/roli-lpci/sigistry-marketplace/blob/a7a30de6bb3e6ba7b60e5b885513721f0a155743/scripts/verify-plugins.mjs
# + .claude-plugin/attestations.json). Written fresh in our style; no donor code copied.
# Code-only scope disclaimer: attestation covers SKILL.md bytes only, not prose claims,
# eval scores, or install safety. Local-only: reads ATTESTATIONS_FILE from disk, never
# fetched from the network (no socket/urllib/requests). Name-collision guard: exact
# case-sensitive skill-name match; slashes, backslashes and ".." never match.
ATTESTATIONS_FILE = ROOT / ".claude-plugin" / "attestations.json"
_ATTESTATIONS_PINNED: dict[str, str] = {}
TRUST_VERIFIED = "verified"
TRUST_UNVERIFIED = "attested-unverified"


def _attestations() -> dict[str, str]:
    """Pinned skill-name -> sha256 map from the local attestations file (local-only)."""
    global _ATTESTATIONS_PINNED
    try:
        raw = json.loads(ATTESTATIONS_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if isinstance(raw, dict) and isinstance(raw.get("skills"), dict):
        raw = raw["skills"]
    if not isinstance(raw, dict):
        return {}
    pinned: dict[str, str] = {}
    for key, val in raw.items():
        if not isinstance(key, str) or not isinstance(val, str):
            continue
        if not key or "/" in key or "\\" in key or ".." in key:
            continue
        pinned[key] = val
    _ATTESTATIONS_PINNED = pinned
    return dict(pinned)


def _skill_sha256(name: str) -> str:
    """Hex sha256 of one skill SKILL.md bytes; empty on missing or bad names."""
    if not isinstance(name, str) or not name:
        return ""
    if "/" in name or "\\" in name or ".." in name:
        return ""
    try:
        data = (_skills_dir() / name / "SKILL.md").read_bytes()
    except OSError:
        return ""
    return hashlib.sha256(data).hexdigest()


def _is_attested(name: str) -> bool:
    """True when live SKILL.md sha matches pinned sha (verify-at-pinned-sha)."""
    if not isinstance(name, str) or not name:
        return False
    if "/" in name or "\\" in name or ".." in name:
        return False
    pinned = _attestations()
    if name not in pinned:
        return False
    expected = pinned[name]
    if not isinstance(expected, str) or not expected:
        return False
    live = _skill_sha256(name)
    if not live:
        return False
    return live.strip().lower() == expected.strip().lower()


def _trust_for(name: str) -> str:
    """Search-result trust field: verified only at pinned sha, else attested-unverified."""
    return TRUST_VERIFIED if _is_attested(name) else TRUST_UNVERIFIED


def _parse_skill_frontmatter(text: str) -> dict:
    """Read version/author/tags from a SKILL.md frontmatter block.

    Defaults mirror book2skill/build.py _frontmatter (0.1.0/skillworks/[])
    so pre-K-18 seeds without versioned frontmatter still rank.
    """
    meta = {"version": "0.1.0", "author": "skillworks", "tags": []}
    if not text.startswith("---"):
        return meta
    parts = text.split("---", 2)
    if len(parts) < 3:
        return meta
    head = parts[1]
    for line in head.splitlines():
        line = line.strip()
        if line.startswith("version:"):
            val = line.split(":", 1)[1].strip()
            if val:
                meta["version"] = val
        elif line.startswith("author:"):
            val = line.split(":", 1)[1].strip()
            if val:
                meta["author"] = val
        elif line.startswith("tags:"):
            val = line.split(":", 1)[1].strip()
            if val.startswith("[") and val.endswith("]"):
                inner = val[1:-1].strip()
                meta["tags"] = [t.strip() for t in inner.split(",") if t.strip()] if inner else []
            elif val:
                meta["tags"] = [val]
    return meta


def _skill_meta(name: str) -> dict:
    """Rank/trust fields for one installed skill (registry ideas only, no paste).

    Donor ideas (MIT, no code copied): pn1024/dsh-skill-market registry
    fields (version/author/downloads/stars/tags/verified) + skillsgate
    trending/install-count rank (extends K-15 gate-first sort). All values
    are derived locally and honestly: frontmatter for version/author/tags,
    eval_report.json for eval_rate/passed, local install state for
    installed/installs. downloads is the eval passed-count proxy (not a real
    registry counter); stars is rate*5 on a 5-star scale; verified equals
    above_gate (rate >= 0.6).
    """
    base = _skills_dir()
    version, author, tags = "0.1.0", "skillworks", []
    try:
        fm = _parse_skill_frontmatter((base / name / "SKILL.md").read_text(encoding="utf-8"))
        version, author, tags = fm["version"], fm["author"], fm["tags"]
    except OSError:
        pass
    rate, passed = 0.0, 0
    try:
        report = json.loads((base / name / "eval_report.json").read_text(encoding="utf-8"))
        rate = float(report.get("rate", 0.0))
        passed = int(report.get("passed", 0))
    except (OSError, ValueError, TypeError, AttributeError):
        pass
    above_gate = rate >= EVAL_GATE
    installed = (base / name / "SKILL.md").exists()
    attested = _is_attested(name)
    trust = TRUST_VERIFIED if attested else TRUST_UNVERIFIED
    return {
        "version": version,
        "author": author,
        "tags": tags,
        "downloads": passed,
        "installs": 1 if installed else 0,
        "stars": round(rate * 5, 1),
        "verified": above_gate,
        "eval_rate": rate,
        "above_gate": above_gate,
        "installed": installed,
        "attested": attested,
        "trust": trust,
    }

_DESCRIPTIONS = {
    "query": "Keywords to search skill markdown for (non-empty string). skill_search is the list entry: use a broad query to browse.",
    "skill": "Optional skill name to restrict search to one skill.",
    "limit": "Max hits to return (integer 1-20, default 5).",
}


def _skills() -> list[str]:
    base = _skills_dir()
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if (p / "SKILL.md").exists())


def _skill_md_files(skill_dir: Path) -> list[Path]:
    """Canonical markdown of one skill: never its export/ output folder, never a link.

    An export/ copy would answer a search four times, and a link that loops back into the
    skill makes a plain recursive walk run into paths of thousands of characters (2026-10-03).
    """
    isjunction = getattr(os.path, "isjunction", None)
    found: list[Path] = []
    for here, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs
                   if not (Path(here) == skill_dir and d == "export")
                   and not os.path.islink(os.path.join(here, d))
                   and not (isjunction and isjunction(os.path.join(here, d)))]
        found += [Path(here) / f for f in files if f.endswith(".md")]
    return sorted(found)


def _search(query: str, skill: str | None = None, limit: int = 5) -> list[dict]:
    base = _skills_dir()
    words = [w.lower() for w in query.split() if len(w) > 2]
    names = [skill] if skill else _skills()
    scored = []
    for name in names:
        meta = _skill_meta(name)
        gate_rank = 1 if meta["above_gate"] else 0
        installed_rank = 1 if meta["installed"] else 0
        for path in _skill_md_files(base / name):
            text = path.read_text(encoding="utf-8")
            low = text.lower()
            score = sum(low.count(w) for w in words)
            if score:
                scored.append((gate_rank, installed_rank, meta["downloads"], score,
                               name, str(path.relative_to(base)), text[:300], meta))
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]), reverse=True)
    return [
        {"skill": n, "file": f, "score": s, "head": h, "version": m["version"],
         "author": m["author"], "downloads": m["downloads"], "installs": m["installs"],
         "stars": m["stars"], "tags": m["tags"], "verified": m["verified"],
         "eval_rate": m["eval_rate"], "above_gate": m["above_gate"],
         "installed": m["installed"], "attested": m["attested"], "trust": m["trust"]}
        for g, ir, d, s, n, f, h, m in scored[:limit]
    ]


def _input_schema() -> dict:
    """Derive skill_search inputSchema from the _search() signature.

    Pattern steal (ideas only, no paste): PrefectHQ/fastmcp @mcp.tool
    auto-schema (Apache-2.0) — types/required from the function so clients
    can validate before calling. Range guard for limit is declared here
    (signature carries no min/max); godot-agent CacheHint shape is separate.
    """
    sig = inspect.signature(_search)
    props: dict = {}
    required: list = []
    for name, param in sig.parameters.items():
        ann = param.annotation
        base = "string"
        if ann is int or (getattr(ann, "__origin__", None) is None and ann == int):
            base = "integer"
        elif name == "limit":
            base = "integer"
        elif name == "query":
            base = "string"
        elif name == "skill":
            base = "string"
        prop: dict = {"type": base, "description": _DESCRIPTIONS.get(name, name)}
        if name == "limit":
            prop.update({"minimum": 1, "maximum": 20, "default": 5})
        props[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}


INPUT_SCHEMA = _input_schema()

PREVIEW_FILES = ("README.md", "SKILL.md")
PREVIEW_HEAD_CHARS = 2000

_PREVIEW_DESCRIPTIONS = {
    "skill": "Skill name to preview (non-empty string, must be an installed skill).",
}


def _preview(skill: str) -> dict:
    """Return inspect-before-install head for one skill.

    README-then-SKILL.md fallback (donor readSkillFile pattern, ideas only):
    serve README.md when present, else SKILL.md. Vol 0 sample stays a
    separate skill file; preview points at the install entrypoint.
    """
    base = _skills_dir()
    for candidate in PREVIEW_FILES:
        path = base / skill / candidate
        if path.exists():
            text = path.read_text(encoding="utf-8")
            return {
                "skill": skill,
                "file": candidate,
                "head": text[:PREVIEW_HEAD_CHARS],
                "chars": len(text),
            }
    return {"skill": skill, "file": "", "head": "", "chars": 0}


def _preview_input_schema() -> dict:
    """Derive skill_preview inputSchema from the _preview() signature."""
    sig = inspect.signature(_preview)
    props: dict = {}
    required: list = []
    for name, param in sig.parameters.items():
        props[name] = {"type": "string", "description": _PREVIEW_DESCRIPTIONS.get(name, name)}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}


PREVIEW_INPUT_SCHEMA = _preview_input_schema()


def _validate_preview_args(args) -> tuple[bool, dict | str]:
    """Validate skill_preview arguments against PREVIEW_INPUT_SCHEMA."""
    if not isinstance(args, dict):
        return False, "arguments must be an object with skill"
    skill = args.get("skill")
    if not isinstance(skill, str) or not skill.strip():
        return False, "skill is required (non-empty string)"
    return True, {"skill": skill}


def _validate_args(args) -> tuple[bool, dict | str]:
    """Validate tools/call arguments against INPUT_SCHEMA. Returns (ok, cleaned|message)."""
    if not isinstance(args, dict):
        return False, "arguments must be an object with query/skill/limit"
    query = args.get("query")
    if not isinstance(query, str) or not query.strip():
        return False, "query is required (non-empty string)"
    skill = args.get("skill")
    if skill is not None and not isinstance(skill, str):
        return False, "skill must be a string when provided"
    limit = args.get("limit", 5)
    try:
        limit = int(limit)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return False, "limit must be integer 1..20"
    if not 1 <= limit <= 20:
        return False, "limit must be integer 1..20"
    return True, {"query": query, "skill": skill, "limit": limit}


def _parse_pinned_name(spec: str) -> tuple[str, str | None]:
    """Split a name@version pin at the last @ (frontmatter version source).

    No @ means unpinned (name, None). Empty name or empty pin falls back
    to the literal spec with no pin so the unknown-skill guard fires.
    """
    if not isinstance(spec, str):
        return "", None
    text = spec.strip()
    if "@" not in text:
        return text, None
    name, _, pinned = text.rpartition("@")
    name, pinned = name.strip(), pinned.strip()
    if not name or not pinned:
        return text, None
    return name, pinned


def _versions_equal(have: str, want: str) -> bool:
    """Dot-part equality: positive-int parts compare as ints, else literal."""
    h, w = have.strip(), want.strip()
    if h == w:
        return True
    hp, wp = h.split("."), w.split(".")
    if len(hp) != len(wp):
        return False
    for a, b in zip(hp, wp):
        if a.isdigit() and b.isdigit() and int(a) > 0 and int(b) > 0:
            if int(a) != int(b):
                return False
        elif a != b:
            return False
    return True


def _install(spec: str) -> dict:
    """Pinned install receipt; refuse on version mismatch, never silent-latest.

    Pin idea steal from VladUZH/wordhoard (licence MIT,
    https://github.com/VladUZH/wordhoard); refuse-unknown-atVersion instead
    of silent-latest is our guard. Written fresh in our style, no donor code
    copied. Version source is local SKILL.md frontmatter via _skill_meta.
    """
    name, pinned = _parse_pinned_name(spec)
    if name not in _skills():
        return {"ok": False, "skill": name or spec, "error": _unknown_skill_message(name or spec)}
    installed = _skill_meta(name)["version"]
    if pinned is not None and not _versions_equal(installed, pinned):
        return {"ok": False, "skill": name, "version": installed, "pinned": pinned,
                "error": f"version mismatch for '{name}': pinned '{pinned}' != installed '{installed}' (refusing install)"}
    return {"ok": True, "skill": name, "version": installed, "pinned": pinned,
            "installed": True, "trust": _trust_for(name)}


_INSTALL_DESCRIPTIONS = {
    "skill": "Skill name with optional @version pin (e.g. progit-branching@0.1.0). Pinned installs refuse on mismatch.",
}


def _install_input_schema() -> dict:
    """Derive skill_install inputSchema from the _install() signature."""
    return {"type": "object", "properties": {
        "skill": {"type": "string", "description": _INSTALL_DESCRIPTIONS["skill"]}}, "required": ["skill"]}


INSTALL_INPUT_SCHEMA = _install_input_schema()


def _validate_install_args(args) -> tuple[bool, dict | str]:
    """Validate skill_install arguments against INSTALL_INPUT_SCHEMA."""
    if not isinstance(args, dict):
        return False, "arguments must be an object with skill"
    skill = args.get("skill")
    if not isinstance(skill, str) or not skill.strip():
        return False, "skill is required (non-empty string, optional name@version pin)"
    return True, {"skill": skill.strip()}


def _error_envelope(message: str) -> dict:
    text = json.dumps({"error": message}, ensure_ascii=False)
    return {
        "content": [{"type": "text", "text": text}],
        "isError": True,
        "is_error": True,
    }
def _reply(iid, result=None, error=None) -> None:
    msg: dict = {"jsonrpc": "2.0", "id": iid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def _unknown_skill_message(skill: str) -> str:
    base = _skills_dir()
    names = _skills()
    return f"unknown skill '{skill}'; serving {len(names)} skills from {base}"


def main(argv: list[str] | None = None) -> None:
    global _CLI_SKILLS_DIR
    cli_args, _ = _build_parser().parse_known_args(list(sys.argv[1:] if argv is None else argv))
    _CLI_SKILLS_DIR = Path(cli_args.skills_dir) if cli_args.skills_dir else None
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = req.get("method")
        iid = req.get("id")
        params = req.get("params", {}) or {}
        if method == "initialize":
            _reply(iid, {"protocolVersion": "2024-11-05", "serverInfo": {"name": "skillworks", "version": "0.1.0"}})
        elif method == "tools/list":
            search_tool = {
                "name": "skill_search",
                "description": "Search built skill markdown by keywords. skill_search is the list entry: use a broad query to browse, then skill_preview to inspect one skill.",
                "inputSchema": INPUT_SCHEMA,
                "_meta": {"cacheHint": CACHE_HINT},
            }
            preview_tool = {
                "name": "skill_preview",
                "description": "Preview one installed skill (README-then-SKILL.md head) before installing. Use to inspect a skill.",
                "inputSchema": PREVIEW_INPUT_SCHEMA,
                "_meta": {"cacheHint": CACHE_HINT},
            }
            install_tool = {
                "name": "skill_install",
                "description": "Install one skill by name with optional @version pin. Pinned installs refuse on mismatch, never silent-latest.",
                "inputSchema": INSTALL_INPUT_SCHEMA,
                "_meta": {"cacheHint": CACHE_HINT},
            }
            _reply(iid, {"tools": [search_tool, preview_tool, install_tool], "_meta": {"cacheHint": CACHE_HINT}})
        elif method == "tools/call":
            if params.get("name") not in ("skill_search", "skill_preview", "skill_install"):
                _reply(iid, error={"code": -32602, "message": "unknown tool"})
                continue
            if params.get("name") == "skill_install":
                args = params.get("arguments", {}) or {}
                ok, cleaned = _validate_install_args(args)
                if not ok:
                    _reply(iid, _error_envelope(cleaned))  # type: ignore[arg-type]
                    continue
                assert isinstance(cleaned, dict)
                result = _install(cleaned["skill"])
                if not result.get("ok"):
                    _reply(iid, _error_envelope(str(result.get("error", "install refused"))))
                    continue
                _reply(iid, {"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]})
                continue
            if params.get("name") == "skill_preview":
                args = params.get("arguments", {}) or {}
                ok, cleaned = _validate_preview_args(args)
                if not ok:
                    _reply(iid, _error_envelope(cleaned))  # type: ignore[arg-type]
                    continue
                assert isinstance(cleaned, dict)
                if cleaned["skill"] not in _skills():
                    _reply(iid, _error_envelope(_unknown_skill_message(cleaned["skill"])))
                    continue
                preview = _preview(cleaned["skill"])
                _reply(iid, {"content": [{"type": "text", "text": json.dumps(preview, ensure_ascii=False)}]})
                continue
            args = params.get("arguments", {}) or {}
            ok, cleaned = _validate_args(args)
            if not ok:
                _reply(iid, _error_envelope(cleaned))  # type: ignore[arg-type]
                continue
            assert isinstance(cleaned, dict)
            if cleaned["skill"] is not None and cleaned["skill"] not in _skills():
                _reply(iid, _error_envelope(_unknown_skill_message(cleaned["skill"])))
                continue
            hits = _search(cleaned["query"], cleaned["skill"], cleaned["limit"])
            _reply(iid, {"content": [{"type": "text", "text": json.dumps(hits, ensure_ascii=False)}]})
        else:
            _reply(iid, error={"code": -32601, "message": "method not found"})


if __name__ == "__main__":
    main()

