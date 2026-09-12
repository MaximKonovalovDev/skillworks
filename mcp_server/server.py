"""Minimal stdio MCP server: skill_search over built skills.

Speaks JSON-RPC over stdio with initialize / tools/list / tools/call.
Tool: skill_search {query, skill?} — substring rank over skill markdown.
No dependencies, no network. Scope is honest: search only, no generation.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"


def _skills() -> list[str]:
    if not SKILLS.exists():
        return []
    return sorted(p.name for p in SKILLS.iterdir() if (p / "SKILL.md").exists())


def _search(query: str, skill: str | None, limit: int = 5) -> list[dict]:
    words = [w.lower() for w in query.split() if len(w) > 2]
    names = [skill] if skill else _skills()
    scored = []
    for name in names:
        for path in sorted((SKILLS / name).rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            low = text.lower()
            score = sum(low.count(w) for w in words)
            if score:
                scored.append((score, name, str(path.relative_to(SKILLS)), text[:300]))
    scored.sort(reverse=True)
    return [
        {"skill": n, "file": f, "score": s, "head": h} for s, n, f, h in scored[:limit]
    ]


def _reply(iid, result=None, error=None) -> None:
    msg: dict = {"jsonrpc": "2.0", "id": iid}
    if error is not None:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()


def main() -> None:
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
            _reply(iid, {"tools": [{"name": "skill_search", "description": "Search built skill markdown by keywords. Use when looking up skill content."}]})
        elif method == "tools/call":
            if params.get("name") != "skill_search":
                _reply(iid, error={"code": -32602, "message": "unknown tool"})
                continue
            args = params.get("arguments", {}) or {}
            hits = _search(args.get("query", ""), args.get("skill"), int(args.get("limit", 5)))
            _reply(iid, {"content": [{"type": "text", "text": json.dumps(hits, ensure_ascii=False)}]})
        else:
            _reply(iid, error={"code": -32601, "message": "method not found"})


if __name__ == "__main__":
    main()
