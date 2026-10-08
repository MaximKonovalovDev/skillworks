"""Video-ffmpeg pack: thin ffmpeg verbs (no binary needed, builds argv)."""
import sys

LICENSE = "MIT"


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


@tool("cut", "cut one segment by start + duration")
def cut(input: str, output: str, start: str = "0", duration: str = "10"):
    return {"cmd": ["ffmpeg", "-y", "-ss", start, "-i", input, "-t", duration, "-c", "copy", output]}


@tool("concat", "join 2+ files into one")
def concat(inputs: list, output: str):
    if not isinstance(inputs, list) or len(inputs) < 2:
        raise ValueError("concat needs a list of 2+ inputs")
    cmd = ["ffmpeg", "-y"]
    for p in inputs:
        cmd += ["-i", p]
    cmd += ["-filter_complex", f"concat=n={len(inputs)}:v=1:a=1", output]
    return {"cmd": cmd}


@tool("overlay", "lay one clip over a base at x:y")
def overlay(base: str, over: str, output: str, x: str = "10", y: str = "10"):
    return {"cmd": ["ffmpeg", "-y", "-i", base, "-i", over, "-filter_complex", f"overlay={x}:{y}", output]}


@tool("clip", "clip one range by start + end")
def clip(input: str, output: str, start: str = "0", end: str = "10"):
    return {"cmd": ["ffmpeg", "-y", "-ss", start, "-to", end, "-i", input, "-c", "copy", output]}


@tool("log_tail", "prove step: tail an ffmpeg log plus PASS/FAIL verdict")
def log_tail(log: str, n: int = 20):
    lines = str(log).splitlines()
    tail = lines[-n:] if n > 0 else []
    verdict = "FAIL" if any("error" in line.lower() for line in tail) else "PASS"
    return {"tail": "\n".join(tail), "verdict": verdict}


def list_tools():
    return list(_TOOLS.values())


def selftest():
    """In-process check: 5 verbs build argv, log_tail proves, registry intact."""
    names = [t.name for t in list_tools()]
    assert names == ["cut", "concat", "overlay", "clip", "log_tail"], f"want 5 tools, got {names}"
    assert _TOOLS["cut"].fn("a.mp4", "b.mp4", "5", "10")["cmd"] == [
        "ffmpeg", "-y", "-ss", "5", "-i", "a.mp4", "-t", "10", "-c", "copy", "b.mp4",
    ]
    assert _TOOLS["clip"].fn("a.mp4", "b.mp4", "5", "15")["cmd"] == [
        "ffmpeg", "-y", "-ss", "5", "-to", "15", "-i", "a.mp4", "-c", "copy", "b.mp4",
    ]
    c = _TOOLS["concat"].fn(["a.mp4", "b.mp4"], "out.mp4")["cmd"]
    assert c[0:2] == ["ffmpeg", "-y"] and "concat=n=2:v=1:a=1" in c
    o = _TOOLS["overlay"].fn("base.mp4", "top.mp4", "out.mp4")["cmd"]
    assert "overlay=10:10" in o
    ok = _TOOLS["log_tail"].fn("frame=1\nframe=2\nvideo:out done")
    assert ok["verdict"] == "PASS" and "frame=2" in ok["tail"]
    bad = _TOOLS["log_tail"].fn("frame=1\nError: no such file")
    assert bad["verdict"] == "FAIL"
    try:
        _TOOLS["concat"].fn(["only.mp4"], "out.mp4")
    except ValueError:
        pass
    else:
        raise AssertionError("concat must refuse fewer than 2 inputs")
    print("SELFTEST PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
