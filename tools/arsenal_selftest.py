"""Real selftests for the arsenal tools of this repo: each tool runs on a fixture in a temp folder.

    python tools/arsenal_selftest.py <book2skill|cron_skip_clean|pipe_dry_run|edit_guard|all>

arsenal.json tested these four tools with `--help`, which only proves the script starts. Here each tool runs the way
arsenal.json declares it (its `run` line) on a small fixture, and its real stdout and exit code are checked: the
passing case and the refusals. Writes only inside a temp folder. Prints one PASS or FAIL line per check and one
RESULT line; exit 0 only when every check of every named tool passes.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]


class Checks:
    def __init__(self, tool: str) -> None:
        self.tool = tool
        self.lines: list[str] = []
        self.failed = 0

    def check(self, ok: bool, what: str, detail: str = "") -> None:
        if ok:
            self.lines.append(f"PASS {self.tool}: {what}")
        else:
            self.failed += 1
            self.lines.append(f"FAIL {self.tool}: {what}" + (f" | got: {detail.strip()[:300]}" if detail else ""))


def declared(tool: str) -> list[str]:
    """The tool's `run` line from arsenal.json with this interpreter in place of `python`."""
    for entry in json.loads((ROOT / "arsenal.json").read_text(encoding="utf-8"))["tools"]:
        if entry["name"] == tool:
            return [sys.executable, *entry["run"][1:]]
    raise SystemExit(f"arsenal.json has no tool {tool!r}")


def run(argv: list[str], text: str | None = None, timeout: int = 120) -> tuple[int, str]:
    """Run argv in the repo folder without a shell; returns (exit code, stdout and stderr)."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    r = subprocess.run(argv, cwd=ROOT, input=text if text is not None else None, stdin=None if text is not None else subprocess.DEVNULL,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env)
    return r.returncode, (r.stdout + r.stderr)


# ---------------------------------------------------------------- cron_skip_clean

def selftest_cron_skip_clean(base: list[str]) -> Checks:
    c = Checks("cron_skip_clean")
    with tempfile.TemporaryDirectory(prefix="arsenal-cron-") as tmp:
        root = Path(tmp)
        watch, state = root / "watch", root / "state" / "w.json"
        (watch / "sub").mkdir(parents=True)
        (watch / "a.txt").write_text("alpha", encoding="utf-8")
        (watch / "sub" / "b.txt").write_text("beta", encoding="utf-8")
        args = ["--watch", str(watch), "--state", str(state)]
        code, out = run([*base, *args])
        first = re.fullmatch(r"RUN ([0-9a-f]{16})\s*", out)
        c.check(code == 0 and first is not None, "first run on a fresh state prints RUN and a 16 hex fingerprint, exit 0", f"{code} {out}")
        fp = first.group(1) if first else ""
        c.check(state.is_file() and json.loads(state.read_text(encoding="utf-8")).get("fingerprint") == fp, "state file holds that fingerprint")
        code, out = run([*base, *args])
        c.check(code == 0 and out.strip() == f"SKIP clean {fp}", "second run on the same folder prints SKIP clean with the same fingerprint, exit 0", f"{code} {out}")
        (watch / "a.txt").write_text("alpha changed", encoding="utf-8")
        code, out = run([*base, *args])
        changed = re.fullmatch(r"RUN ([0-9a-f]{16})\s*", out)
        c.check(code == 0 and changed is not None and changed.group(1) != fp, "an edited file prints RUN with a new fingerprint", f"{code} {out}")
        code, out = run([*base, *args])
        c.check(out.startswith("SKIP clean"), "the run after that is clean again", out)
        (watch / "sub" / "new.txt").write_text("new", encoding="utf-8")
        code, out = run([*base, *args])
        c.check(out.startswith("RUN "), "a new file prints RUN", out)
        state.parent.mkdir(parents=True, exist_ok=True)
        state.write_text("{ not json", encoding="utf-8")
        code, out = run([*base, *args])
        c.check(code == 0 and out.startswith("RUN "), "an unreadable state file counts as dirty, not as a crash", f"{code} {out}")
        inside = watch / "state.json"
        code, out = run([*base, "--watch", str(watch), "--state", str(inside)])
        c.check(code == 2 and out.startswith("ERROR refused") and not inside.exists(), "a state file inside the watch folder is refused (exit 2) and not written", f"{code} {out}")
        code, out = run([*base, "--watch", str(root / "missing"), "--state", str(state)])
        c.check(code == 2 and out.startswith("ERROR watch dir missing"), "a missing watch folder is refused with exit 2", f"{code} {out}")
    return c


# ---------------------------------------------------------------- pipe_dry_run

def selftest_pipe_dry_run(base: list[str]) -> Checks:
    c = Checks("pipe_dry_run")
    real = [a for a in base if a != "--dry-run"]  # same script, the non-dry path, for the refusals
    with tempfile.TemporaryDirectory(prefix="arsenal-pipe-") as tmp:
        root = Path(tmp)
        src, out_dir = root / "in", root / "out"
        (src / "nested").mkdir(parents=True)
        (src / "a.txt").write_bytes(b"abc\r\n" * 100)   # 400 characters once a line break counts as one: 100 tokens (125 if bytes were counted)
        (src / "b.txt").write_text("x" * 800, encoding="utf-8")   # 200 tokens
        (src / "c.txt").write_text("y" * 1200, encoding="utf-8")  # 300 tokens
        (src / "skip.md").write_text("z" * 4000, encoding="utf-8")        # not .txt
        (src / "nested" / "d.txt").write_text("w" * 4000, encoding="utf-8")  # not top level
        args = lambda cap: ["--input", str(src), "--out", str(out_dir), "--cap", str(cap)]  # noqa: E731
        code, out = run([*base, *args(1000)])
        c.check(code == 0 and out.strip() == "DRY-RUN 3 items spend 600 tokens (cap 1000)", "dry run counts the 3 top-level .txt items at chars // 4 (CRLF as one character): 600 tokens", f"{code} {out}")
        c.check(not out_dir.exists(), "dry run writes nothing: the out folder does not exist")
        code, out = run([*base, *args(100)])
        c.check(code == 0 and out.strip() == "DRY-RUN 3 items spend 600 tokens (cap 100)", "a dry run over the cap only reports, exit 0", f"{code} {out}")
        code, out = run([*real, *args(500)])
        c.check(code == 2 and out.startswith("ERROR over cap: spend 600 tokens > cap 500") and not out_dir.exists(), "a real run over the cap is refused with exit 2 and writes nothing", f"{code} {out}")
        code, out = run([*real, *args(1000)])
        receipt = out_dir / "receipt.json"
        ok = code == 0 and out.strip() == "RUN 3 items spend 600/1000 tokens" and receipt.is_file()
        c.check(ok, "a real run within the cap prints RUN 3 items spend 600/1000 tokens, exit 0", f"{code} {out}")
        copied = sorted(p.name for p in out_dir.iterdir()) if out_dir.is_dir() else []
        c.check(copied == ["a.txt", "b.txt", "c.txt", "receipt.json"], "it copies exactly the 3 items and a receipt", str(copied))
        c.check(ok and json.loads(receipt.read_text(encoding="utf-8")) == {"tool": "pipe-run", "items": 3, "spend": 600, "cap": 1000}, "the receipt carries items, spend and cap")
        code, out = run([*base, "--input", str(root / "missing"), "--out", str(out_dir), "--cap", "10"])
        c.check(code == 2 and out.startswith("ERROR input dir missing"), "a missing input folder is refused with exit 2", f"{code} {out}")
        code, out = run([*base, "--input", str(src), "--out", str(src), "--cap", "10"])
        c.check(code == 2 and out.startswith("ERROR refused: --out is the input dir"), "an out folder equal to the input folder is refused", f"{code} {out}")
        (src / "bad.txt").write_bytes(b"\xff\xfe\x00 not utf-8 \xc3")
        code, out = run([*base, *args(1000)])
        c.check(code == 2 and "is not UTF-8 text; nothing written" in out, "a file that is not UTF-8 is refused with exit 2", f"{code} {out}")
    return c


# ---------------------------------------------------------------- edit_guard

def selftest_edit_guard(base: list[str]) -> Checks:
    c = Checks("edit_guard")
    with tempfile.TemporaryDirectory(prefix="arsenal-edit-") as tmp:
        root = Path(tmp)
        target = root / "target.txt"
        raw = b"alpha\r\n\tbeta two\r\ngamma\r\n"
        target.write_bytes(raw)
        old_file = root / "old.txt"

        def guard(*extra: str, text: str | None = None) -> tuple[int, str]:
            return run([*base, str(target), *extra], text=text)

        old_file.write_bytes(b"\tbeta two\r\ngamma")
        code, out = guard("--old-file", str(old_file))
        c.check(code == 0 and out.startswith("EDIT GUARD PASS") and "endings CRLF" in out and "matches 1" in out, "an oldString that is there exactly (tab and CRLF) passes and names the file's endings", f"{code} {out}")
        code, out = guard("--old-string", "alpha")
        c.check(code == 0 and "EDIT GUARD PASS" in out, "a one-line --old-string passes", f"{code} {out}")
        code, out = guard(text="gamma")
        c.check(code == 0 and "EDIT GUARD PASS" in out, "an oldString on stdin passes", f"{code} {out}")
        code, out = guard("--old-string", "m")
        c.check(code == 0 and "matches 2" in out, "it counts how many times the oldString occurs", f"{code} {out}")
        old_file.write_bytes(b"alpha\n\tbeta two\n")
        code, out = guard("--old-file", str(old_file))
        c.check(code == 1 and "refused: oldString not found" in out and "hint: file is CRLF" in out, "an LF oldString against a CRLF file is refused (exit 1) with the CRLF hint", f"{code} {out}")
        code, out = guard("--old-string", "    beta two")
        c.check(code == 1 and "hint: file uses tabs but oldString uses spaces" in out and "closest line 2" in out and "\\tbeta two" in out, "spaces for a tab are refused and the closest line is quoted with the tab as \\t", f"{code} {out}")
        code, out = guard("--old-string", "delta")
        c.check(code == 1 and "re-read the file before editing" in out, "text that is not in the file is refused and quotes the re-read rule", f"{code} {out}")
        code, out = guard(text="")
        c.check(code == 1 and "empty oldString" in out, "an empty oldString is refused", f"{code} {out}")
        code, out = run([*base, str(root / "nope.txt"), "--old-string", "x"])
        c.check(code == 1 and "cannot read" in out, "a missing target file is refused with exit 1", f"{code} {out}")
        c.check(target.read_bytes() == raw, "the target file is byte for byte the same after every call (it writes nothing)")
    return c


# ---------------------------------------------------------------- book2skill

BOOK = """# Lease Guide

## Chapter 1: Leases

A lease guards a queue item. A worker claims the lease before it works. When the worker dies the lease expires and the item is requeued.

## Chapter 2: Requeue

Requeue puts a stuck item back at the end of the line. The retry counter grows by one on each requeue. After three retries the item is parked.
"""


def selftest_book2skill(base: list[str]) -> Checks:
    c = Checks("book2skill")
    with tempfile.TemporaryDirectory(prefix="arsenal-b2s-") as tmp:
        root = Path(tmp)
        book, work, skill = root / "book.md", root / "work" / "leaseguide", root / "skills" / "leaseguide"
        book.write_bytes(BOOK.encode("utf-8"))  # LF on every system
        good, bad = root / "good_qa.jsonl", root / "bad_qa.jsonl"
        good.write_text(json.dumps({"q": "what happens when the worker dies", "must": ["lease", "requeue"]}) + "\n", encoding="utf-8")
        bad.write_text(json.dumps({"q": "what is the zebra speed", "must": ["zebra", "furlong"]}) + "\n", encoding="utf-8")
        code, out = run([*base, "extract", "--in", str(book), "--out", str(work)])
        receipt = work / "receipt.json"
        got = json.loads(receipt.read_text(encoding="utf-8")) if receipt.is_file() else {}
        chars = len(BOOK.strip())  # extract trims the ends
        c.check(code == 0 and out.startswith(f"extracted {chars} chars (text") and got.get("stage") == "extract" and got.get("chars") == chars, "extract reads the book and writes a receipt with the character count", f"{code} {out}")
        code, out = run([*base, "split", "--work", str(work)])
        c.check(code == 0 and out.strip() == "split into 1 chunks" and (work / "chunks" / "0000.txt").is_file(), "split cuts it into 1 chunk file", f"{code} {out}")
        code, out = run([*base, "index", "--work", str(work)])
        index = work / "index.jsonl"
        c.check(code == 0 and out.strip() == "indexed 1 records" and index.is_file() and len(index.read_text(encoding="utf-8").splitlines()) == 1, "index writes one grounded record per chunk", f"{code} {out}")
        desc = "Use when a queue item is stuck: leases and requeue"
        code, out = run([*base, "build", "--work", str(work), "--skill", str(skill), "--name", "leaseguide", "--description", desc])
        skill_md = (skill / "SKILL.md").read_text(encoding="utf-8") if (skill / "SKILL.md").is_file() else ""
        c.check(code == 0 and out.startswith("built ") and re.search(r"(?m)^name: leaseguide$", skill_md) is not None and "description:" in skill_md, "build writes a SKILL.md whose name matches its folder and which has a description", f"{code} {out}")
        c.check((skill / "references" / "sources.md").is_file(), "build writes references/sources.md")
        code, out = run([*base, "build", "--work", str(work), "--skill", str(root / "skills" / "wrongdir"), "--name", "leaseguide", "--description", desc])
        c.check(code == 2 and "must match skill dir" in out and not (root / "skills" / "wrongdir").exists(), "build refuses a name that differs from its folder (exit 2) and writes nothing", f"{code} {out}")
        code, out = run([*base, "eval", "--work", str(work), "--skill", str(skill), "--qa", str(good)])
        rep = json.loads(out[out.index("{"):]) if "{" in out else {}
        c.check(code == 0 and rep.get("rate") == 1.0 and rep.get("graded_on") == "skill", "eval passes a question the skill's own text answers: rate 1.0, graded on the skill", f"{code} {out}")
        code, out = run([*base, "eval", "--work", str(work), "--skill", str(skill), "--qa", str(bad)])
        rep = json.loads(out[out.index("{"):]) if "{" in out else {}
        c.check(rep.get("rate") == 0.0 and rep.get("passed") == 0, "eval fails a question the skill cannot answer: rate 0.0", f"{code} {out}")
        code, out = run([*base, "audit", "--skill", str(skill)])
        rep = json.loads(out[out.index("{"):]) if "{" in out else {}
        c.check(code == 0 and rep.get("body_budget") == 2000 and rep.get("over_budget") is False and rep.get("total_tokens", 0) > 0, "audit prints the token cost, the 2000 token body budget and over_budget false", f"{code} {out[:200]}")
        code, out = run([*base, "refresh", "--work", str(work)])
        code2, out2 = run([*base, "refresh", "--work", str(work)])
        c.check(code == 0 and code2 == 0 and out2.strip() == "unchanged, no-op", "refresh on an unchanged source is a no-op the second time", f"{out.strip()} / {out2.strip()}")
        code, out = run([*base, "extract", "--in", str(root / "nonexistent.md"), "--out", str(root / "work" / "nx")])
        c.check(code == 2 and "not found" in out, "extract of a missing source is refused with exit 2", f"{code} {out}")
    return c


TESTS: dict[str, Callable[[list[str]], Checks]] = {
    "book2skill": selftest_book2skill,
    "cron_skip_clean": selftest_cron_skip_clean,
    "pipe_dry_run": selftest_pipe_dry_run,
    "edit_guard": selftest_edit_guard,
}


def main(argv: list[str]) -> int:
    names = list(TESTS) if argv == ["all"] else argv
    if not names or any(n not in TESTS for n in names):
        print(f"usage: python tools/arsenal_selftest.py <{'|'.join(TESTS)}|all>")
        return 2
    failed = total = 0
    for name in names:
        result = TESTS[name](declared(name))
        for line in result.lines:
            print(line)
        failed += result.failed
        total += len(result.lines)
    print(f"RESULT {'FAIL' if failed else 'PASS'}: {', '.join(names)} ({total - failed} of {total} checks pass)")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
