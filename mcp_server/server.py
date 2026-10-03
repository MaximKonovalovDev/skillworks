"""Minimal stdio MCP server: skill_search + skill_preview over built skills.

Speaks JSON-RPC over stdio with initialize / tools/list / tools/call.
Tools: skill_search {query, skill?} — substring rank over skill markdown;
  skill_preview {skill} — README-then-SKILL.md fallback head for inspect-before-install.
No dependencies, no network. Scope is honest: search + preview only, no generation.
"""
from __future__ import annotations

import inspect
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"

SKILLS_DIR_ENV_VARS = ("SKILLWORKS_SKILLS_DIR", "SKILLS_DIR")

_CLI_SKILLS_DIR: Path | None = None


def _parse_skills_dir_override(argv: list[str]) -> Path | None:
    for i, arg in enumerate(argv):
        if arg == "--skills-dir" and i + 1 < len(argv):
            return Path(argv[i + 1])
        if arg.startswith("--skills-dir="):
            return Path(arg.split("=", 1)[1])
    return None


def _skills_dir() -> Path:
    if _CLI_SKILLS_DIR is not None:
        return _CLI_SKILLS_DIR
    for var in SKILLS_DIR_ENV_VARS:
        val = os.environ.get(var)
        if val:
            return Path(val)
    return SKILLS

CACHE_HINT = {"ttlMs": 3600000, "scope": "public"}

_DESCRIPTIONS = {
    "query": "Keywords to search skill markdown for (non-empty string).",
    "skill": "Optional skill name to restrict search to one skill.",
    "limit": "Max hits to return (integer 1-20, default 5).",
}


def _skills() -> list[str]:
    base = _skills_dir()
    if not base.exists():
        return []
    return sorted(p.name for p in base.iterdir() if (p / "SKILL.md").exists())


def _search(query: str, skill: str | None = None, limit: int = 5) -> list[dict]:
    base = _skills_dir()
    words = [w.lower() for w in query.split() if len(w) > 2]
    names = [skill] if skill else _skills()
    scored = []
    for name in names:
        for path in sorted((base / name).rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            low = text.lower()
            score = sum(low.count(w) for w in words)
            if score:
                scored.append((score, name, str(path.relative_to(base)), text[:300]))
    scored.sort(reverse=True)
    return [
        {"skill": n, "file": f, "score": s, "head": h} for s, n, f, h in scored[:limit]
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
    _CLI_SKILLS_DIR = _parse_skills_dir_override(list(sys.argv[1:] if argv is None else argv))
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
                "description": "Search built skill markdown by keywords. Use when looking up skill content.",
                "inputSchema": INPUT_SCHEMA,
                "_meta": {"cacheHint": CACHE_HINT},
            }
            preview_tool = {
                "name": "skill_preview",
                "description": "Preview one installed skill (README-then-SKILL.md head) before installing. Use to inspect a skill.",
                "inputSchema": PREVIEW_INPUT_SCHEMA,
                "_meta": {"cacheHint": CACHE_HINT},
            }
            _reply(iid, {"tools": [search_tool, preview_tool], "_meta": {"cacheHint": CACHE_HINT}})
        elif method == "tools/call":
            if params.get("name") not in ("skill_search", "skill_preview"):
                _reply(iid, error={"code": -32602, "message": "unknown tool"})
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
