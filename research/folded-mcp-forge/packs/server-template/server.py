"""forge server template (python-sdk FastMCP shape). Proof: python server.py --selftest."""
import asyncio
import sys

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("forge-template")
ALLOWED = {"ping", "add", "echo"}


@mcp.tool()
def ping() -> str:
    """Liveness check."""
    return "pong"


@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two ints."""
    return a + b


@mcp.tool()
def echo(text: str) -> str:
    """Echo back text."""
    return text


async def selftest() -> None:
    tools = await mcp.list_tools()
    names = sorted(t.name for t in tools)
    assert names == ["add", "echo", "ping"], f"want 3 tools, got {names}"
    assert set(names) == ALLOWED, f"allow-list drift: {names}"
    # Direct calls through the tool manager (no transport needed).
    ctx = mcp.get_context()
    out = await mcp._tool_manager.call_tool("ping", {}, context=ctx, convert_result=True)
    assert out, "ping returned empty"
    # Deny: unknown tool must fail, never run.
    denied = False
    try:
        await mcp._tool_manager.call_tool("rm_rf", {}, context=ctx, convert_result=True)
    except Exception:
        denied = True
    assert denied, "deny test failed: unknown tool did not raise"
    print(f"SELFTEST PASS: tools={','.join(names)} deny=ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        asyncio.run(selftest())
    else:
        mcp.run()
