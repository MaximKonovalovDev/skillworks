"""MCP template: ToolBinding shape + duplicate guard."""
import sys

class ToolBinding:
    def __init__(self, name, fn, description=""):
        self.name = name
        self.fn = fn
        self.description = description

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
    """In-process check: 3 tools, verbs work, registry intact."""
    names = [t.name for t in list_tools()]
    assert names == ["ping", "add", "echo"], f"want 3 tools, got {names}"
    assert _TOOLS["ping"].fn() == "pong"
    assert _TOOLS["add"].fn(2, 3) == 5
    assert _TOOLS["echo"].fn("hi") == "hi"
    print("SELFTEST PASS")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
