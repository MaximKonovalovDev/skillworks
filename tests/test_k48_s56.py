"""K-48 slices (5)+(6): stub/demo/vision honesty (F2P red before, green after).

Slice (5): no 174 B broken patterns.md stub survives (deleted where stub,
kept where real, e.g. james-psychology-briefer).
Slice (6): demo/demo.gif is real (>10 KB) or the Demo line is gone
(design-studio order O-025 already open for the real GIF, no second order);
VISION-TABLES.md carries one measured number per row (progit 1.0,
freud 0.833 live).
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BROKEN_FRAGMENTS = ("\\chapters/notes.md\\", "eferences/sources.md\\")
STALE_FREUD = ("6/12=0.5", "6/12 = 0.5", "0.5 gate-held")


def test_patterns_no_174b_stub() -> None:
    """No skills/*/patterns.md is the 174 B broken stub."""
    bad: list[str] = []
    for path in sorted((ROOT / "skills").glob("*/patterns.md")):
        try:
            data = path.read_bytes()
        except OSError:
            continue
        text = data.decode("utf-8", errors="replace")
        if len(data) == 174 and any(f in text for f in BROKEN_FRAGMENTS):
            bad.append(f"{path.parent.name}/patterns.md is the 174 B broken stub")
    assert not bad, "; ".join(bad)


def test_demo_real_or_absent() -> None:
    """demo.gif is real (>10 KB) or absent with no Demo line pointing at it."""
    skill = ROOT / "skills" / "progit-branching"
    gif = skill / "demo" / "demo.gif"
    listing = (skill / "listing.md").read_text(encoding="utf-8") if (skill / "listing.md").is_file() else ""
    problems: list[str] = []
    if gif.is_file():
        size = gif.stat().st_size
        if size <= 10 * 1024:
            problems.append(f"demo/demo.gif is a {size} B placeholder, not a real demo")
    if "demo/demo.gif" in listing:
        problems.append("listing.md still carries a Demo line pointing at demo/demo.gif")
    assert not problems, "; ".join(problems)


def test_vision_one_measured_number() -> None:
    """VISION-TABLES.md names one live number per row (freud 0.833, not 0.5)."""
    text = (ROOT / "VISION-TABLES.md").read_text(encoding="utf-8")
    stale = [s for s in STALE_FREUD if s in text]
    assert not stale, f"stale freud numbers remain: {stale}"
    assert "10/12=0.833" in text or "10/12 = 0.833" in text, "live freud 10/12=0.833 missing"
