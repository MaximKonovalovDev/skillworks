"""Run every bad/good pair of references/pairs.json in pwsh 7, the way the loops' shell runs commands.

Each side runs as its own script block in its own scratch copy of the
fixture under $env:TEMP/opencode (never in the repo, never in another
repo's tree). A bad side must throw the miss line it names, or silently
query the wrong file; a good side must print the PASS report it promises.

    python skills/hyperfine-bench/scripts/run_hyperfine.py          # one line per pair
    python skills/hyperfine-bench/scripts/run_hyperfine.py --json   # machine readable
    python skills/hyperfine-bench/scripts/run_hyperfine.py --pair hb-p01

Exit code 0 when every bad pair fails or lies and every good pair prints
what it promises.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = HERE.parent / "references" / "pairs.json"

DRIVER = r"""
param([string]$InFile, [string]$OutFile)
$__items = Get-Content -LiteralPath $InFile -Raw | ConvertFrom-Json
$__results = foreach ($__it in $__items) {
  Set-Location -LiteralPath $__it.dir
  $global:LASTEXITCODE = 0
  $Error.Clear()
  $__text = ''
  $__threw = $null
  try {
    $__sb = [scriptblock]::Create($__it.cmd)
    $__text = (& $__sb *>&1 | Out-String)
  } catch {
    $__threw = $_.Exception.GetType().Name + ': ' + $_.Exception.Message
    $__text = $__text + $__threw
  }
  [pscustomobject]@{ key = $__it.key; text = $__text; threw = $__threw; errors = $Error.Count; exit = $LASTEXITCODE }
}
$__results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutFile -Encoding utf8
"""


def scratch_root() -> Path:
    base = Path(os.environ.get("TEMP") or tempfile.gettempdir()) / "opencode"
    base.mkdir(parents=True, exist_ok=True)
    return Path(tempfile.mkdtemp(prefix="hb-pairs-", dir=str(base)))


def run_pairs(doc: dict) -> list[dict]:
    pwsh = shutil.which("pwsh")
    if not pwsh:
        raise RuntimeError("pwsh 7 is not installed")
    root = scratch_root()
    items = []
    for pair in doc["pairs"]:
        for side in ("bad", "good"):
            cmd = pair.get(side)
            if cmd is None:
                continue
            d = root / f"{pair['id']}-{side}"
            for rel, body in doc["fixture"].items():
                f = d / rel
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(body.encode("utf-8"))
            items.append({"key": f"{pair['id']}|{side}", "cmd": cmd, "dir": str(d)})
    (root / "in.json").write_text(json.dumps(items), encoding="utf-8")
    (root / "driver.ps1").write_text(DRIVER, encoding="utf-8")
    env = dict(os.environ)
    proc = subprocess.run(
        [pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-File", str(root / "driver.ps1"), str(root / "in.json"), str(root / "out.json")],
        env=env, capture_output=True, text=True, timeout=300,
    )
    out = root / "out.json"
    if not out.exists():
        raise RuntimeError(f"driver failed: {proc.stdout[-400:]} {proc.stderr[-400:]}")
    raw = json.loads(out.read_text(encoding="utf-8-sig"))
    got = {r["key"]: r for r in (raw if isinstance(raw, list) else [raw])}
    results = []
    for pair in doc["pairs"]:
        res = {"id": pair["id"], "skipped": None, "bad_ok": None, "good_ok": None, "why": [], "bad_text": ""}
        if pair.get("bad") is not None:
            r = got[f"{pair['id']}|bad"]
            text = (r["text"] or "")
            res["bad_text"] = text
            failed = bool(r["threw"]) or (r["errors"] or 0) > 0 or (r["exit"] or 0) != 0
            if pair.get("bad_silent"):
                res["bad_ok"] = pair["expect"] not in text
                if not res["bad_ok"]:
                    res["why"].append("bad printed the right answer, it was meant to give a wrong one")
            else:
                hit = re.search(pair["bad_error"], text, re.I) is not None
                res["bad_ok"] = failed and hit
                if not failed:
                    res["why"].append("bad did not fail")
                elif not hit:
                    res["why"].append(f"bad failed with another message: {text.strip()[:160]!r}")
        if pair.get("good") is not None:
            r = got[f"{pair['id']}|good"]
            text = (r["text"] or "")
            clean = not r["threw"] and (r["errors"] or 0) == 0
            if "expect_regex" in pair:
                found = re.search(pair["expect_regex"], text, re.M) is not None
            else:
                found = pair["expect"] in text
            res["good_ok"] = clean and found
            if not clean:
                res["why"].append(f"good raised an error: {text.strip()[:160]!r}")
            elif not found:
                res["why"].append(f"good printed {text.strip()[:160]!r}")
        results.append(res)
    shutil.rmtree(root, ignore_errors=True)
    return results


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Replay the hyperfine-bench bad/good pairs in pwsh 7.")
    ap.add_argument("--json", action="store_true", help="machine-readable results")
    ap.add_argument("--pair", default=None, help="run one pair by id")
    args = ap.parse_args(argv)
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    if args.pair:
        doc["pairs"] = [p for p in doc["pairs"] if p["id"] == args.pair]
        if not doc["pairs"]:
            print(f"unknown pair {args.pair}")
            return 2
    results = run_pairs(doc)
    if args.json:
        print(json.dumps(results, indent=1))
    bad = 0
    for r in results:
        if r["skipped"]:
            line = f"SKIP {r['id']} ({r['skipped']})"
        else:
            ok = r["bad_ok"] is not False and r["good_ok"] is not False
            bad += 0 if ok else 1
            line = f"{'PASS' if ok else 'FAIL'} {r['id']} {'; '.join(r['why'])}"
        if not args.json:
            print(line)
    print(f"{len(results) - bad} of {len(results)} pairs behave as written")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
