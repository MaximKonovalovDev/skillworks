"""Selftest: verbs ping/add/echo + duplicate guard."""
import server

assert [t.name for t in server.list_tools()] == ["ping", "add", "echo"]
assert server._TOOLS["ping"].fn() == "pong"
assert server._TOOLS["add"].fn(2, 3) == 5
assert server._TOOLS["echo"].fn("hi") == "hi"

@server.tool("ping", "dup attempt")
def ping_dup():
    return "evil"

assert server._TOOLS["ping"].fn() == "pong", "duplicate overwrote original"
print("SELFTEST PASS")
