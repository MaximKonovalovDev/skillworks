"""Run every bad/good pair of references/pairs.json in pwsh 7, the way the loops' shell runs commands.

The shell tool starts `pwsh -NoLogo -NoProfile -NonInteractive -Command <text>`. Here one pwsh
process runs every pair, each as its own script block in its own copy of the fixture folder,
with Git's usr/bin removed from PATH (the setup where grep, head, tail, wc and sed fail).

    python skills/pwsh-for-bash-writers/scripts/run_pairs.py          # prints one line per pair
    python skills/pwsh-for-bash-writers/scripts/run_pairs.py --json   # machine readable

Exit code 0 when every bad pair fails or lies and every good pair prints what it promises.
"""
from __future__ import annotations

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

TOOLS = ("node", "rg", "python", "curl.exe", "pwsh", "powershell")


def stripped_path() -> str:
    """PATH without Git's usr/bin and mingw64 (where grep.exe, head.exe, wc.exe, sed.exe live)."""
    parts = os.environ.get("PATH", "").split(os.pathsep)
    return os.pathsep.join(p for p in parts if not re.search(r"[\\/]Git[\\/](usr|mingw64)", p, re.I))


def missing_tools(cmd: str) -> list[str]:
    path = stripped_path()
    return [t for t in TOOLS if re.search(rf"(^|[\s;|(&]){re.escape(t)}(\s|$)", cmd) and not shutil.which(t, path=path)]


def run_pairs(doc: dict) -> list[dict]:
    pwsh = shutil.which("pwsh")
    if not pwsh:
        raise RuntimeError("pwsh 7 is not installed")
    root = Path(tempfile.mkdtemp(prefix="pairs-"))
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
    env = dict(os.environ, PATH=stripped_path())
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
        gone = sorted({t for side in ("bad", "good") if pair.get(side) for t in missing_tools(pair[side])})
        if gone:
            res["skipped"] = "needs " + ", ".join(gone)
            results.append(res)
            continue
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


def main(argv: list[str]) -> int:
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    results = run_pairs(doc)
    if "--json" in argv:
        print(json.dumps(results, indent=1))
    bad = 0
    for r in results:
        if r["skipped"]:
            line = f"SKIP {r['id']} ({r['skipped']})"
        else:
            ok = r["bad_ok"] is not False and r["good_ok"] is not False
            bad += 0 if ok else 1
            line = f"{'PASS' if ok else 'FAIL'} {r['id']} {'; '.join(r['why'])}"
        if "--json" not in argv:
            print(line)
    print(f"{len(results) - bad} of {len(results)} pairs behave as written")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
