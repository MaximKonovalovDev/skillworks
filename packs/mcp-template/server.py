"""MCP template: the ONE FastMCP-shape template (dependency-free, ideas only).

Tool auto-schema from signature + CacheHint (fastmcp ideas only, no paste;
donor PrefectHQ/fastmcp Apache-2.0 auto-schema + godot-agent MIT CacheHint shape).

Deprecated toward this file: mcp_server/server.py and
research/folded-mcp-forge/packs/server-template/server.py. Use this file for new work.
"""
import inspect
import sys

CACHE_HINT = {"ttlMs": 3600000, "scope": "public"}


def _schema_for(fn):
    """Derive JSON inputSchema from fn signature (fastmcp @mcp.tool idea, no paste)."""
    props = {}
    required = []
    for name, param in inspect.signature(fn).parameters.items():
        ann = param.annotation
        if ann is int:
            kind = "integer"
        elif ann is float:
            kind = "number"
        elif ann is bool:
            kind = "boolean"
        else:
            kind = "string"
        props[name] = {"type": kind}
        if param.default is inspect.Parameter.empty:
            required.append(name)
    return {"type": "object", "properties": props, "required": required}


class ToolBinding:
    def __init__(self, name, fn, description=""):
        self.name = name
        self.fn = fn
        self.description = description
        self.inputSchema = _schema_for(fn)
        self.cacheHint = CACHE_HINT

_TOOLS = {}
WARN_ON_DUPLICATE = True

def tool(name, description=""):
    def deco(fn):
        if name in _TOOLS:
            if WARN_ON_DUPLICATE:
                print(f"duplicate tool '{name}' kept original, rejected new", file=sys.stderr)
            return fn
        _TOOLS[name] = ToolBinding(name, fn, description)
        return fn
    return deco

@tool("ping", "liveness check")
def ping():
    return "pong"

@tool("add", "add two numbers")
def add(a: float, b: float):
    return a + b

@tool("echo", "echo text back")
def echo(text: str):
    return text

def list_tools():
    return list(_TOOLS.values())

def selftest():
    """In-process check: 3 tools, verbs work, registry intact, schema + CacheHint."""
    names = [t.name for t in list_tools()]
    assert names == ["ping", "add", "echo"], f"want 3 tools, got {names}"
    assert _TOOLS["ping"].fn() == "pong"
    assert _TOOLS["add"].fn(2, 3) == 5
    assert _TOOLS["echo"].fn("hi") == "hi"
    assert _TOOLS["ping"].inputSchema == {"type": "object", "properties": {}, "required": []}
    assert set(_TOOLS["add"].inputSchema["properties"]) == {"a", "b"}
    assert _TOOLS["add"].inputSchema["required"] == ["a", "b"]
    assert _TOOLS["echo"].inputSchema["required"] == ["text"]
    assert CACHE_HINT == {"ttlMs": 3600000, "scope": "public"}
    assert all(t.cacheHint == CACHE_HINT for t in list_tools())
    print("SELFTEST PASS")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
