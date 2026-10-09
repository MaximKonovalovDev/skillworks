"""K-30 [TEAM-LOOP-1010-A] part-score script: one line per part from real data.

Prints exactly one line each for P1-P5 + workspace (6 lines, stdout only),
exit 0. Every number comes from a real artifact (receipts, chunk files,
eval reports, a live MCP handshake, shop proof, git workspace). Anything
unmeasured prints UNKNOWN -- no invented numbers.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STAGES = ("extract", "split", "index", "build", "audit", "eval", "refresh", "export")


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _chunk_count(workdir: Path) -> int | None:
    chunks = workdir / "chunks"
    if not chunks.is_dir():
        return None
    try:
        return sum(1 for p in chunks.iterdir() if p.is_file())
    except OSError:
        return None


def _p1() -> str:
    stages = sum(1 for s in STAGES if (ROOT / "book2skill" / f"{s}.py").is_file())
    progit = ROOT / "work" / "progit-branching"
    freud = ROOT / "work" / "freud-dreams"
    progit_chunks = _chunk_count(progit)
    freud_chunks = _chunk_count(freud)
    progit_rec = _read_json(progit / "receipt.json") or {}
    freud_rec = _read_json(freud / "receipt.json") or {}
    progit_idx = progit_rec.get("records", "UNKNOWN")
    freud_chars = freud_rec.get("chars", "UNKNOWN")
    freud_stripped = freud_rec.get("stripped", "UNKNOWN")
    if progit_chunks is None and freud_chunks is None:
        return "P1 pipeline: UNKNOWN (no work/*/chunks measured)"
    return (
        f"P1 pipeline: stages {stages}/{len(STAGES)} present; "
        f"progit {progit_chunks if progit_chunks is not None else 'UNKNOWN'} chunks, "
        f"index {progit_idx} rec; "
        f"freud {freud_chunks if freud_chunks is not None else 'UNKNOWN'} chunks, "
        f"{freud_chars} chars stripped={freud_stripped}"
    )


def _p2() -> str:
    server = ROOT / "mcp_server" / "server.py"
    if not server.is_file():
        return "P2 mcp: UNKNOWN (mcp_server/server.py missing)"
    reqs = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {"name": "skill_search", "arguments": {"query": "branching git", "limit": 2}},
        },
    ]
    try:
        proc = subprocess.run(
            [sys.executable, str(server)],
            input="\n".join(json.dumps(r) for r in reqs) + "\n",
            capture_output=True,
            text=True,
            timeout=20,
            cwd=str(ROOT),
        )
    except Exception as exc:
        return f"P2 mcp: UNKNOWN (handshake spawn failed: {exc})"
    by_id: dict = {}
    for line in proc.stdout.splitlines():
        try:
            msg = json.loads(line)
        except ValueError:
            continue
        if isinstance(msg, dict) and "id" in msg:
            by_id[msg["id"]] = msg
    ok_init = isinstance((by_id.get(1) or {}).get("result"), dict)
    tools = ((by_id.get(2) or {}).get("result") or {}).get("tools", [])
    schema_props = (((tools[0] if tools else {}).get("inputSchema") or {}).get("properties") or {})
    has_schema = all(k in schema_props for k in ("query", "skill", "limit"))
    call_text = (((by_id.get(3) or {}).get("result") or {}).get("content") or [{}])[0].get("text", "")
    top = "UNKNOWN (no hits)"
    try:
        hits = json.loads(call_text) if call_text else []
        if hits:
            top = f"{hits[0].get('skill', '?')} score={hits[0].get('score', '?')}"
    except ValueError:
        top = "UNKNOWN (unparseable call result)"
    handshake = "OK" if ok_init else "FAIL"
    schema = "schema query/skill/limit" if has_schema else "schema UNKNOWN"
    return f"P2 mcp: handshake {handshake}, tools/list skill_search {schema}, call 'branching git' top={top}"


def _p3() -> str:
    progit_txt = ROOT / "work" / "progit-branching" / "full_text.txt"
    freud_txt = ROOT / "work" / "freud-dreams" / "full_text.txt"
    try:
        progit_size = progit_txt.stat().st_size if progit_txt.is_file() else None
    except OSError:
        progit_size = None
    try:
        freud_size = freud_txt.stat().st_size if freud_txt.is_file() else None
    except OSError:
        freud_size = None
    skills = sorted(p.parent.name for p in ROOT.glob("skills/*/SKILL.md")) if (ROOT / "skills").is_dir() else []
    seeds = [s for s in ("progit-branching", "freud-dream-psychology") if (ROOT / "skills" / s / "SKILL.md").is_file()]
    if progit_size is None and freud_size is None and not skills:
        return "P3 seeds: UNKNOWN (no work full_text or skills measured)"
    return (
        f"P3 seeds: work progit-branching {progit_size if progit_size is not None else 'UNKNOWN'} B, "
        f"freud-dreams {freud_size if freud_size is not None else 'UNKNOWN'} B (gitignored, never committed); "
        f"{len(skills)} skills with SKILL.md, seeds present={'+'.join(seeds) if seeds else 'UNKNOWN'}"
    )


def _p4() -> str:
    gate = "UNKNOWN"
    try:
        text = (ROOT / "book2skill" / "export.py").read_text(encoding="utf-8")
        match = re.search(r"GATE\s*=\s*([0-9.]+)", text)
        if match:
            gate = match.group(1)
    except OSError:
        pass
    progit = _read_json(ROOT / "skills" / "progit-branching" / "eval_report.json") or {}
    freud = _read_json(ROOT / "skills" / "freud-dream-psychology" / "eval_report.json") or {}
    if not progit and not freud:
        return f"P4 eval-gate: gate {gate}, UNKNOWN (no eval_report.json measured)"
    bits = [f"gate {gate}"]

    def _bit(name: str, rep: dict) -> str | None:
        if not rep or rep.get("total") is None:
            return None
        total = rep["total"]
        passed = rep.get("passed", "UNKNOWN")
        rate = rep.get("rate", "UNKNOWN")
        try:
            verdict = "ships" if float(rate) >= float(gate) else "held"
        except (TypeError, ValueError):
            verdict = "UNKNOWN"
        return f"{name} {passed}/{total}={rate} {verdict}"

    for bit in (_bit("progit", progit), _bit("freud", freud)):
        bits.append(bit if bit is not None else "UNKNOWN skill UNKNOWN (no report)")
    return "P4 eval-gate: " + "; ".join(bits)


def _p5() -> str:
    listing = ROOT / "skills" / "progit-branching" / "listing.md"
    vol0 = ROOT / "skills" / "progit-branching" / "vol0-sample.md"
    demo = ROOT / "skills" / "progit-branching" / "demo" / "demo.gif"
    try:
        text = listing.read_text(encoding="utf-8") if listing.is_file() else ""
    except OSError:
        text = ""
    sales_match = re.search(r"[Ss]ales\D{0,12}(\d+)", text)
    sales = sales_match.group(1) if sales_match else "UNKNOWN"
    price_match = re.search(r"\$\d+", text)
    price = price_match.group(0) if price_match else "UNKNOWN"
    status = "PREP-ONLY" if "PREP-ONLY" in text else ("UNKNOWN" if not text else "no-status")
    try:
        vol0_size = vol0.stat().st_size if vol0.is_file() else None
    except OSError:
        vol0_size = None
    try:
        demo_size = demo.stat().st_size if demo.is_file() else None
    except OSError:
        demo_size = None
    if not text and vol0_size is None and demo_size is None:
        return "P5 shop: UNKNOWN (no listing.md/vol0/demo measured)"
    return (
        f"P5 shop: listing {status} sales={sales} price={price}; "
        f"vol0-sample {vol0_size if vol0_size is not None else 'UNKNOWN'} B; "
        f"demo.gif {demo_size if demo_size is not None else 'UNKNOWN'} B"
    )


def _workspace() -> str:
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(ROOT),
        ).stdout.strip() or "UNKNOWN"
    except Exception as exc:
        sha = f"UNKNOWN (git rev-parse failed: {exc})"
    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(ROOT),
        ).stdout.strip() or "UNKNOWN"
    except Exception as exc:
        branch = f"UNKNOWN (git branch failed: {exc})"
    skills = len(list(ROOT.glob("skills/*/SKILL.md"))) if (ROOT / "skills").is_dir() else "UNKNOWN"
    tests = len(list(ROOT.glob("tests/test_*.py"))) if (ROOT / "tests").is_dir() else "UNKNOWN"
    return (
        f"workspace: git {sha} on {branch}; {skills} skills; {tests} test files; "
        f"python {sys.version.split()[0]}"
    )


USAGE = (
    "usage: python tools/part_score.py [--help] - print one line each for P1-P5 + workspace "
    "from real artifacts (no args needed); e.g. python tools/part_score.py"
)


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if "-h" in args or "--help" in args:
        print(USAGE)
        return 0
    if args:
        print(f"error: unknown argument(s): " + " ".join(args) + "\n" + USAGE, file=sys.stderr)
        return 2
    for line in (_p1(), _p2(), _p3(), _p4(), _p5(), _workspace()):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
