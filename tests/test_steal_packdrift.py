"""Steal packdrift: listing title and licence lines must agree with pack.json."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import pack_check as pc

PACK = {
    "slug": "fix-pack",
    "title": "Fix Pack",
    "version": "1.0.0",
    "price_usd": 9,
    "skills": [
        {"name": "alpha", "licence": "MIT", "credit": "own work"},
        {"name": "beta", "licence": "MIT and Apache-2.0", "credit": "own work"},
    ],
    "vol0": {"name": "free-one", "licence": "CC-BY-NC-SA-3.0", "credit": "free"},
}

LISTING = """# Fix Pack

## Licences

- `alpha`: MIT.
- `beta`: MIT and Apache-2.0.
"""


def fails(rep: pc.Report) -> list:
    return [w for lv, w in rep.lines if lv == "FAIL"]


def test_matching_pack_passes() -> None:
    rep = pc.Report()
    pc.check_listing_drift(PACK, LISTING, rep)
    assert fails(rep) == []


def test_title_drift_fails() -> None:
    rep = pc.Report()
    pc.check_listing_drift(PACK, LISTING.replace("# Fix Pack", "# Other Pack"), rep)
    assert any("title-drift" in w for w in fails(rep))


def test_licence_drift_fails() -> None:
    rep = pc.Report()
    drifted = LISTING.replace("`beta`: MIT and Apache-2.0.", "`beta`: MIT.")
    pc.check_listing_drift(PACK, drifted, rep)
    assert any("licence-drift" in w for w in fails(rep))