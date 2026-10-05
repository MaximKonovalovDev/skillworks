"""Stranger sale gate for Fleet Vol 1: the checks a buyer could redo.

A stranger with this repo can prove the pack for sale is what the listing
says, in about 5 minutes (plus the 15-minute install run in SHOP_PROOF.md):

    python tools/vol1_stranger_check.py

What it checks, one PASS/FAIL line each, then one RESULT line (exit 0 on PASS):

  clean HEAD     `git status --porcelain` is empty on packs/, skills/ and
                 tools/, so the bytes are the shipped ones, not a local edit
  pack_check     `tools/pack_check.py packs/fleet-vol-1` replayed in process;
                 every FAIL there fails here too
  vol0 free      the Vol 0 skill is not one of the paid skills (Pro Git is
                 NonCommercial: free forever, never sold)
  price agrees   listing.md Price, price.txt and pack.json name the same $N
  3 pages        the Price evidence section links 3 or more seller pages,
                 else FAIL (liveness is pack_check's verdict, replayed above)

Usage: python tools/vol1_stranger_check.py [--offline] [--no-factory]
(--offline skips fetching the evidence pages, --no-factory skips the factory
buyer-file gate; both are passed through to pack_check).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import pack_check as pc  # noqa: E402

PACK_DIR = ROOT / "packs" / "fleet-vol-1"
CLEAN_PATHS = ("packs", "skills", "tools")


def clean_head() -> tuple[bool, str]:
    """True when git status is empty on packs/, skills/ and tools/."""
    try:
        r = subprocess.run(["git", "status", "--porcelain", "--", *CLEAN_PATHS],
                           cwd=ROOT, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as err:
        return False, f"git status did not run ({err})"
    if r.returncode != 0:
        return False, f"git status exit {r.returncode}: {(r.stderr or '').strip()[:120]}"
    dirty = [ln for ln in (r.stdout or "").splitlines() if ln.strip()]
    if dirty:
        shown = "; ".join(dirty[:3])
        return False, f"{len(dirty)} dirty paths on packs/skills/tools ({shown})"
    return True, "packs/, skills/ and tools/ match HEAD"


def vol0_free(pack: dict) -> tuple[bool, str]:
    """True when the Vol 0 skill is not one of the paid skills."""
    vol0 = (pack.get("vol0") or {}).get("name", "")
    paid = [s.get("name", "") for s in pack.get("skills", [])]
    if not vol0:
        return False, "pack.json names no vol0 skill"
    if vol0 in paid:
        return False, f"Vol 0 skill {vol0!r} is also a paid skill: free forever, never sold"
    return True, f"Vol 0 {vol0!r} is not in the paid skills ({', '.join(paid)})"


def price_agrees(pack: dict) -> tuple[bool, str]:
    """True when listing.md, price.txt and pack.json name the same $N."""
    listing = (PACK_DIR / "listing.md").read_text(encoding="utf-8")
    stated = pc.field(listing, "Price")
    price_txt = PACK_DIR / "price.txt"
    canon = price_txt.read_text(encoding="utf-8") if price_txt.is_file() else ""
    want = float(pack["price_usd"])
    got = [pc.PRICE.search(t or "") for t in (stated, canon)]
    if not all(got) or any(float(g[1]) != want for g in got if g):
        return False, (f"price differs: listing says {stated!r}, price.txt says {canon.strip()!r}, "
                       f"pack.json says ${want:g}")
    return True, f"${want:g} in listing.md, price.txt and pack.json"


def three_pages() -> tuple[bool, str]:
    """True when the Price evidence section links 3 or more seller pages."""
    listing = (PACK_DIR / "listing.md").read_text(encoding="utf-8")
    section = next((v for k, v in pc.sections_of(listing).items() if k.startswith("price evidence")), "")
    urls = sorted(set(u.rstrip(".,;:") for u in pc.URL.findall(section)))
    if len(urls) < 3:
        return False, f"price evidence links {len(urls)} seller pages, want 3 or more"
    return True, f"price evidence links {len(urls)} seller pages"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true", help="do not fetch the price evidence pages")
    ap.add_argument("--no-factory", action="store_true", help="skip the factory buyer-file gate")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    fails = 0

    def say(ok: bool, what: str) -> None:
        nonlocal fails
        print(f"{'PASS' if ok else 'FAIL'} {what}")
        fails += 0 if ok else 1

    say(*clean_head())

    rep = pc.check_pack(PACK_DIR, offline=args.offline, factory=not args.no_factory)
    for level, what in rep.lines:
        print(f"{level} {what}")
    pack_fails = rep.count("FAIL")
    fails += pack_fails
    pack = None
    if pack_fails == 0:
        print("PASS pack_check: replayed, no FAIL")
    try:
        pack = json.loads((PACK_DIR / "pack.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        print(f"FAIL pack.json: cannot read ({err})")
        fails += 1
    if pack is not None:
        say(*vol0_free(pack))
        try:
            say(*price_agrees(pack))
        except OSError as err:
            say(False, f"price files unreadable ({err})")
    try:
        say(*three_pages())
    except OSError as err:
        say(False, f"listing.md unreadable ({err})")

    print(f"RESULT {'FAIL' if fails else 'PASS'}: fleet-vol-1 stranger sale gate"
          + (f" ({fails} findings)" if fails else " (clean HEAD, pack_check replayed, vol0 free, price agrees, 3 pages)"))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
