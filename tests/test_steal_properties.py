# Attribution: strategy shape ported from python-attrs/attrs (MIT,
# https://github.com/python-attrs/attrs). Attrs keeps shared Hypothesis
# builders in tests/strategies.py (@st.composite / st.builds / st.recursive
# feeding @given); this file rebuilds that shape in this repo style for
# pack names/prices/tags/frontmatter. No donor code copied.
"""Property-based pack-gate checks: generated names/prices/tags/frontmatter.

The good fixture mirrors tests/test_pack_check.py (same LISTING shape, same
make_skill/fix/run helpers). Each property resets its files per example, so
examples stay independent inside one tmp repo, and listing-only mutations need
no rebuild (the paid zip carries no price or listing text).
"""
import json
import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

import skill_gates as g

sys.path.insert(0, str(g.ROOT / "tools"))
import pack_build as pb  # noqa: E402
import pack_check as pc  # noqa: E402

MAX_EXAMPLES = 20

LISTING = """# Fix Pack

Status: store-ready except the store assets below. Not live.
Price: $9
AI disclosure: generated: text written by an AI agent and checked by tests.
Category: Tool
Tags: a, b
Author: tester
Repository: https://example.com/repo
Stars: 0
Weekly installs: 0
Sales: 0

## What is inside

- `alpha`: does a thing.
- `beta`: does another.

## Requirements

Node 24.

## Install

Copy the folders.

## Price evidence

- https://shop.example/one: costs $12.
- https://shop.example/two: costs $20.
- https://shop.example/three: costs $9.

## Licences

- `alpha`: MIT.
- `beta`: MIT and Apache-2.0.

## Proof

- `alpha`: 2026-10-03, 3 passed.
- `beta`: 2026-10-03, 4 passed.

## Store assets

- cover: needed: a PNG cover.
- demo: needed: a GIF of the session.
- screenshots: needed: three PNG captures.

## Free sample (Vol 0)

`free-one`, CC-BY-NC-SA-3.0, free.
"""


def make_skill(root: Path, name: str, passed: int, licence: str = "MIT") -> None:
    d = root / "skills" / name
    (d / "references").mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Use when testing {name}.\nlicense: {licence}\n---\n\nBody of {name}. See `references/more.md`.\n", encoding="utf-8")
    (d / "references" / "more.md").write_text("more\n", encoding="utf-8")
    (d / "references" / "live-proof.json").write_text(json.dumps({"skill": name, "date": "2026-10-03T18:55Z", "result": f"{passed} passed in 1.00s"}), encoding="utf-8")


@pytest.fixture()
def fix(tmp_path: Path) -> dict:
    root = tmp_path / "repo"
    for name, n in (("alpha", 3), ("beta", 4)):
        make_skill(root, name, n)
    make_skill(root, "free-one", 2, "CC-BY-NC-SA-3.0")
    pack_dir = root / "packs" / "fix-pack"
    pack_dir.mkdir(parents=True)
    pack = {"slug": "fix-pack", "title": "Fix Pack", "version": "1.0.0", "price_usd": 9,
            "skills": [{"name": "alpha", "licence": "MIT", "credit": "own work"},
                       {"name": "beta", "licence": "MIT and Apache-2.0", "credit": "own work and facts from a repo"}],
            "vol0": {"name": "free-one", "licence": "CC-BY-NC-SA-3.0", "credit": "derived from a book, free, never sold"}}
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    (pack_dir / "price.txt").write_text("$9\n", encoding="utf-8")
    (pack_dir / "README-buyer.md").write_text("# Fix Pack\n\nUnzip and copy `skills/`.\n", encoding="utf-8")
    (pack_dir / "listing.md").write_text(LISTING, encoding="utf-8")
    dist = root / "dist"
    pb.build(pack_dir, dist, root / "skills")
    return {"root": root, "pack_dir": pack_dir, "dist": dist, "pack": pack}


def run(fix: dict, **kw) -> pc.Report:
    kw.setdefault("offline", True)
    kw.setdefault("skill_problems", lambda name: [])
    return pc.check_pack(fix["pack_dir"], root=fix["root"], dist=fix["dist"], **kw)


def fails(rep: pc.Report) -> list[str]:
    return [w for lv, w in rep.lines if lv == "FAIL"]


def _reset_listing_shape(fix: dict) -> None:
    (fix["pack_dir"] / "listing.md").write_text(LISTING, encoding="utf-8")
    (fix["pack_dir"] / "price.txt").write_text("$9\n", encoding="utf-8")
    path = fix["pack_dir"] / "pack.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    d["price_usd"] = 9
    path.write_text(json.dumps(d), encoding="utf-8")


def _set_all_prices(fix: dict, price: int) -> None:
    path = fix["pack_dir"] / "pack.json"
    d = json.loads(path.read_text(encoding="utf-8"))
    d["price_usd"] = price
    path.write_text(json.dumps(d), encoding="utf-8")
    listing = fix["pack_dir"] / "listing.md"
    listing.write_text(re.sub(r"(?m)^Price:.*$", f"Price: ${price}", listing.read_text(encoding="utf-8")), encoding="utf-8")
    (fix["pack_dir"] / "price.txt").write_text(f"${price}\n", encoding="utf-8")


@st.composite
def slug_strategy(draw) -> str:
    head = draw(st.sampled_from("abcdefghijklmnopqrstuvwxyz"))
    tail = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz0123456789-", min_size=2, max_size=12))
    return head + tail


tag_word = st.from_regex(r"[a-z]{2,6}", fullmatch=True)
tag_tree = st.recursive(tag_word, lambda inner: st.lists(inner, min_size=1, max_size=2), max_leaves=5)


def flatten_tags(tree) -> list[str]:
    if isinstance(tree, str):
        return [tree]
    out: list[str] = []
    for branch in tree:
        out.extend(flatten_tags(branch))
    return out


@dataclass(frozen=True)
class SkillFrontmatter:
    name: str
    licence: str


frontmatter_strategy = st.builds(
    SkillFrontmatter,
    name=st.from_regex(r"[a-z][a-z0-9-]{2,10}", fullmatch=True),
    licence=st.sampled_from(["MIT", "Apache-2.0", "BSD-3-Clause", "ISC", "CC0", "CC-BY-NC-SA-3.0"]),
)


@given(price=st.integers(min_value=1, max_value=499))
@settings(max_examples=MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_listing_price_must_match_pack_json_and_price_txt(fix: dict, price: int) -> None:
    """Agreeing prices pass; a listing price that differs fails the price check."""
    _reset_listing_shape(fix)
    _set_all_prices(fix, price)
    assert fails(run(fix)) == []
    listing = fix["pack_dir"] / "listing.md"
    listing.write_text(
        re.sub(r"(?m)^Price:.*$", f"Price: ${price + 1}", listing.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    assert any(w.startswith("price:") for w in fails(run(fix)))


@given(field_name=st.sampled_from(sorted(pc.FIELDS)), tree=tag_tree)
@settings(max_examples=MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_generated_tags_pass_and_a_dropped_field_fails(fix: dict, field_name: str, tree) -> None:
    """Generated Tags keep the good pack passing; dropping any required field fails."""
    _reset_listing_shape(fix)
    flat = [t for t in flatten_tags(tree) if t not in ("todo", "tbd")]
    assume(flat)
    tags_line = ", ".join(flat)[:64]
    assume(tags_line.strip())
    assume(pc.PRIVATE.search(tags_line) is None)
    listing = fix["pack_dir"] / "listing.md"
    listing.write_text(
        re.sub(r"(?m)^Tags:.*$", f"Tags: {tags_line}", listing.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    assert fails(run(fix)) == []
    text = listing.read_text(encoding="utf-8")
    listing.write_text("\n".join(ln for ln in text.splitlines() if not ln.startswith(field_name + ":")), encoding="utf-8")
    assert any(f"field {field_name}:" in w for w in fails(run(fix)))


@given(fm=frontmatter_strategy, slug=slug_strategy())
@settings(max_examples=MAX_EXAMPLES, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_frontmatter_licence_and_slug_rules(fix: dict, fm: SkillFrontmatter, slug: str) -> None:
    """A NonCommercial frontmatter licence fails the skill gate; a pack slug
    outside its folder name fails the manifest gate, the folder name passes."""
    pack_path = fix["pack_dir"] / "pack.json"
    pack = json.loads(pack_path.read_text(encoding="utf-8"))
    (fix["root"] / "skills" / "alpha" / "SKILL.md").write_text(
        f"---\nname: {fm.name}\ndescription: Use when testing {fm.name}.\nlicense: {fm.licence}\n---\n\nBody.\n",
        encoding="utf-8",
    )
    rep = pc.Report()
    pc.check_skills(pack, fix["root"] / "skills", rep, lambda name: [])
    skill_fails = [w for lv, w in rep.lines if lv == "FAIL"]
    if pc.NC.search(fm.licence):
        assert any("NonCommercial source" in w for w in skill_fails)
    else:
        assert not any("NonCommercial source" in w for w in skill_fails)
    pack["slug"] = slug
    pack_path.write_text(json.dumps(pack), encoding="utf-8")
    manifest_rep = pc.Report()
    out = pc.check_manifest(fix["pack_dir"], manifest_rep)
    manifest_fails = [w for lv, w in manifest_rep.lines if lv == "FAIL"]
    if slug != fix["pack_dir"].name:
        assert out is None
        assert any("is not the folder name" in w for w in manifest_fails)
    else:
        assert out is not None
        assert not any("is not the folder name" in w for w in manifest_fails)


def test_property_case_budget_reports_count() -> None:
    total = 3 * MAX_EXAMPLES
    warnings.warn(f"property budget: {total} generated cases across 3 properties ({MAX_EXAMPLES} each)", stacklevel=1)
    assert total >= 40
