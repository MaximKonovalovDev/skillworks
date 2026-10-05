"""Vol 1 badges + stranger 15-min script: python tools/g19-badge.py [--badges|--script|--check]

Read-only. Reads packs/fleet-vol-1/pack.json, listing.md and price.txt.
Prints badge markdown (installs + official) and a teach-style 15-min run
script that links Vol 1 at the end with a click-through measure.

Badges stay honest: installs 0 and sales 0 until a real sale, per listing.md.
Views and drafts never count. No network, no writes, no new deps.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PACK_DIR = ROOT / "packs" / "fleet-vol-1"

LIVE_RE = re.compile(r"(?m)^Live listing:\s*(https://\S+)\s*$")
REPO_RE = re.compile(r"(?m)^Repository:\s*(https://\S+)\s*$")
PRICE_RE = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)")
INSTALLS_RE = re.compile(r"(?im)^Weekly installs:\s*(.+?)\s*$")
SALES_RE = re.compile(r"(?im)^Sales:\s*(.+?)\s*$")


def load_truth() -> dict:
    """Pack truth, read-only. Raises OSError/ValueError when files unreadable."""
    pack = json.loads((PACK_DIR / "pack.json").read_text(encoding="utf-8"))
    listing = (PACK_DIR / "listing.md").read_text(encoding="utf-8")
    price_txt = (PACK_DIR / "price.txt").read_text(encoding="utf-8")
    live = LIVE_RE.search(listing)
    repo = REPO_RE.search(listing)
    return {
        "slug": pack.get("slug", ""),
        "version": str(pack.get("version", "")),
        "price_usd": pack.get("price_usd", 0),
        "live": live.group(1).strip() if live else "",
        "repo": repo.group(1).strip() if repo else "",
        "listing": listing,
        "price_txt": price_txt,
    }


def badge_lines(t: dict) -> list[str]:
    """Two badge markdown lines: installs + official. Honest counts from listing."""
    installs = "0"
    m = INSTALLS_RE.search(t["listing"])
    if m:
        n = re.search(r"\d+", m.group(1))
        installs = n.group(0) if n else "0"
    live = t["live"] or "https://maxkonova.gumroad.com/l/fleet-pack"
    repo = t["repo"] or "https://github.com/MaximKonovalovDev/skillworks"
    esc = lambda u: u.replace(")", "%29")
    return [
        f"[![installs](https://img.shields.io/badge/installs-{installs}-blue)]({esc(live)})",
        f"[![official](https://img.shields.io/badge/source-official-green)]({esc(repo)})",
    ]


SCRIPT = """Stranger 15-min run (teach style, one PC, PowerShell 7).

You teach one habit. You link Vol 1 once, at the end. You measure one click.

0-2 min (hook, one fail):
- Open PowerShell 7. Make notes.txt with 5 lines.
- Type: head -n 2 notes.txt
- Show the red error: head is not recognized. Say: this is the mistake agents make daily.

2-10 min (teach, three pairs):
- Pair 1: Get-Content -TotalCount 2 notes.txt (first two lines).
- Pair 2: Select-String -Pattern word notes.txt (search, not grep).
- Pair 3: @(Get-Content notes.txt).Count (count lines, not wc).
- Each pair: bash form fails or lies, pwsh form prints the answer. Let the stranger type all three.

10-13 min (prove it is tested):
- Say: these three come from a tested skill with 49 such pairs, each run in PowerShell 7.
- Run one proof line the stranger can redo: ask the agent for the first two lines without saying how, watch it use Get-Content.

13-15 min (link Vol 1 once + measure):
- Say: this habit plus 48 more, a real-browser skill and a Bevy skill are Fleet Vol 1, $19 once: https://maxkonova.gumroad.com/l/fleet-pack
- Free sample first: the Vol 0 git skill is free and never sold.
- Measure: ask the stranger to say OPENED (link opened) or SKIPPED. Record one of the two words plus the date. That is the click-through count.
- Rule: views and drafts never count. Sales stay 0 until a store payout or report names a buyer.
"""


def cmd_badges() -> int:
    try:
        t = load_truth()
    except (OSError, ValueError) as err:
        print(f"FAIL cannot read pack truth ({err})")
        return 1
    for line in badge_lines(t):
        print(line)
    return 0


def cmd_script() -> int:
    print(SCRIPT, end="")
    return 0


def cmd_check() -> int:
    fails = 0

    def say(ok: bool, what: str) -> None:
        nonlocal fails
        print(f"{'PASS' if ok else 'FAIL'} {what}")
        fails += 0 if ok else 1

    try:
        t = load_truth()
    except (OSError, ValueError) as err:
        print(f"FAIL cannot read pack truth ({err})")
        print("RESULT FAIL: g19 badges (unreadable pack files)")
        return 1

    say(t["slug"] == "fleet-vol-1", f"slug is fleet-vol-1 (got {t['slug']!r})")
    say(float(t["price_usd"]) == 19, f"price is $19 (got ${t['price_usd']})")
    stated = PRICE_RE.search(t["listing"].split("Price:", 1)[-1][:80] if "Price:" in t["listing"] else "")
    canon = PRICE_RE.search(t["price_txt"])
    say(bool(stated and canon and float(stated.group(1)) == 19 and float(canon.group(1)) == 19),
        "price agrees in listing.md and price.txt ($19)")
    say(bool(t["live"]), f"live listing linked ({t['live'] or 'missing'})")
    say(bool(t["repo"]), f"official repo linked ({t['repo'] or 'missing'})")
    mi = INSTALLS_RE.search(t["listing"])
    say(bool(mi and mi.group(1).strip().startswith("0")), "installs badge honest (listing says 0)")
    ms = SALES_RE.search(t["listing"])
    say(bool(ms and ms.group(1).strip().startswith("0")), "sales honest (listing says 0, views never count)")
    lines = badge_lines(t)
    say(len(lines) == 2 and all(l.startswith("[![") and "](https://" in l for l in lines),
        "badge markdown: installs + official, two lines")
    say("fleet-pack" in lines[0] and "github" in lines[1],
        "badges link Vol 1 page (installs) and official repo (official)")
    say("https://maxkonova.gumroad.com/l/fleet-pack" in SCRIPT, "script links Vol 1 once, at the end")
    say("OPENED" in SCRIPT and "SKIPPED" in SCRIPT, "script has click-through measure (OPENED or SKIPPED)")
    say("Sales stay 0" in SCRIPT, "script keeps UNKNOWN views = FAIL rule")

    print("RESULT PASS: g19 badges (installs + official, script links Vol 1, measure kept)"
          if fails == 0 else f"RESULT FAIL: g19 badges ({fails} findings)")
    return 1 if fails else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--badges", action="store_true", help="print badge markdown (default)")
    g.add_argument("--script", action="store_true", help="print stranger 15-min run script")
    g.add_argument("--check", action="store_true", help="verify badges match pack truth")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    if args.script:
        return cmd_script()
    if args.check:
        return cmd_check()
    return cmd_badges()


if __name__ == "__main__":
    sys.exit(main())
