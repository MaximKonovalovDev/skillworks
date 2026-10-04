"""K-48 slice (2): no NonCommercial sample carries a price.

F2P: skills/progit-branching/vol0-sample.md line 5 still says
"paid Vol 1 ($10, 0 sales so far)" -> this test fails.
After: the Vol 0 sample shares the full skill free under the same
CC BY-NC-SA licence, with no $N and no paid-Vol-1 line -> passes.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRICE_RE = re.compile(r"\$\d")
PAID_VOL_RE = re.compile(r"paid\s+vol\s*1", re.I)

NC_SKILLS = ["progit-branching", "git-one-branch"]


def _nc_files(skill: str) -> list[Path]:
    d = ROOT / "skills" / skill
    return [d / "vol0-sample.md", d / "listing.md"]


def test_nc_vol0_samples_carry_no_price():
    offenders: list[str] = []
    for skill in NC_SKILLS:
        for path in _nc_files(skill):
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if PRICE_RE.search(text):
                offenders.append(f"{path.name} names a price ({PRICE_RE.search(text).group(0)})")
            if PAID_VOL_RE.search(text):
                offenders.append(f"{path.name} advertises a paid Vol 1")
    assert not offenders, f"NonCommercial sample carries a price: {'; '.join(offenders)}"


def test_progit_vol0_is_free_under_same_licence():
    vol0 = ROOT / "skills" / "progit-branching" / "vol0-sample.md"
    text = vol0.read_text(encoding="utf-8")
    assert "CC BY-NC-SA" in text
    assert "never sold" in text or "shared free" in text or "Share freely" in text
