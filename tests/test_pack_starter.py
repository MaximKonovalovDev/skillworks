"""python tools/pack_build.py <pack> --starter: the listing set of a new pack, prefilled from pack.json, with slot lines for the rest."""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g
from test_pack_check import make_skill

sys.path.insert(0, str(g.ROOT / "tools"))
import pack_build as pb  # noqa: E402
import pack_check as pc  # noqa: E402

REAL_PACK = g.ROOT / "packs" / "fleet-vol-1"
H2 = re.compile(r"(?m)^## (.+?)\s*$")


@pytest.fixture()
def world(tmp_path: Path) -> dict:
    root = tmp_path / "repo"
    for name, n in (("alpha", 3), ("beta", 4)):
        make_skill(root, name, n)
    make_skill(root, "free-one", 2, "CC-BY-NC-SA-3.0")
    pack_dir = root / "packs" / "fix-pack"
    pack_dir.mkdir(parents=True)
    pack = {"slug": "fix-pack", "title": "Fix Pack: two tested skills", "version": "1.0.0", "price_usd": 9,
            "skills": [{"name": "alpha", "licence": "MIT", "credit": "own work"},
                       {"name": "beta", "licence": "MIT and Apache-2.0", "credit": "own work and facts from a repo"}],
            "vol0": {"name": "free-one", "licence": "CC-BY-NC-SA-3.0", "credit": "Derived from a book, free, never sold."}}
    (pack_dir / "pack.json").write_text(json.dumps(pack, indent=2), encoding="utf-8")
    return {"root": root, "pack_dir": pack_dir, "dist": root / "dist", "pack": pack, "skills": root / "skills"}


def stamp(world: dict, today: str = "2026-10-04") -> dict[str, str]:
    pb.write_starters(world["pack_dir"], world["skills"], today)
    return {n: (world["pack_dir"] / n).read_text(encoding="utf-8") for n in pb.STARTER_FILES}


def check(world: dict) -> pc.Report:
    pb.build(world["pack_dir"], world["dist"], world["skills"])
    return pc.check_pack(world["pack_dir"], root=world["root"], dist=world["dist"], offline=True, skill_problems=lambda name: [], factory=False)


def fails(rep: pc.Report) -> list[str]:
    return [w for lv, w in rep.lines if lv == "FAIL"]


def test_the_starter_has_every_heading_and_field_the_gate_requires_from_one_constant(world: dict) -> None:
    files = stamp(world)
    assert sorted(files) == sorted(pb.STARTER_FILES) == sorted(p.name for p in world["pack_dir"].iterdir() if p.name != "pack.json")
    listing = files["listing.md"]
    assert H2.findall(listing) == [h for h, _ in pb.LISTING_SECTIONS] and len(pb.LISTING_SECTIONS) == 12
    assert pc.SECTIONS is pb.REQUIRED_SECTIONS and pc.FIELDS is pb.LISTING_FIELDS, "pack_check reads the constants the starter is written from"
    secs = pc.sections_of(listing)
    assert [s for s in pc.SECTIONS if not any(k.startswith(s) for k in secs)] == []
    assert [f for f in pc.FIELDS if pc.field(listing, f) is None] == []
    assert listing.startswith("# Fix Pack: two tested skills\n")


def test_the_starter_headings_are_the_ones_of_the_real_pack() -> None:
    real = (REAL_PACK / "listing.md").read_text(encoding="utf-8")
    assert H2.findall(real) == [h for h, _ in pb.LISTING_SECTIONS]
    for name in ("README-buyer.md", "vol0-sample.md"):
        real_text = (REAL_PACK / name).read_text(encoding="utf-8")
        fake = {"slug": "x-pack", "title": "X Pack: t", "version": "1.0.0", "price_usd": 5,
                "skills": [{"name": "s", "licence": "MIT", "credit": "c"}], "vol0": {"name": "v", "licence": "MIT", "credit": "c"}}
        text = pb.readme_starter(fake) if name == "README-buyer.md" else pb.vol0_starter(fake)
        assert H2.findall(text) == H2.findall(real_text), name


def test_the_starter_is_prefilled_from_pack_json_and_the_live_proofs(world: dict) -> None:
    (world["skills"] / "beta" / "references" / "live-proof.json").unlink()  # a skill with no proof gets a slot, not an invented line
    files = stamp(world, today="2026-10-05")
    listing = files["listing.md"]
    assert "Price: $9\n" in listing and "version 1.0.0" in listing and "`fix-pack.zip`" in listing and "The pack is 2 skills" in listing
    assert "- `alpha`: MIT. " in listing and "- `beta`: MIT and Apache-2.0. " in listing
    assert "`free-one`" in listing and "CC-BY-NC-SA-3.0" in listing and "- 2026-10-05: version 1.0.0 assembled." in listing
    assert "- `alpha`: 2026-10-03, 3 passed (" in listing
    beta_proof = next(ln for ln in listing.splitlines() if ln.startswith("- `beta`: ") and "live-proof.json" in ln)
    assert "{{slot:" in beta_proof and "passed (" not in beta_proof
    assert files["price.txt"] == "$9\n"
    assert "CC-BY-NC-SA-3.0" in files["vol0-sample.md"] and "Derived from a book" in files["vol0-sample.md"] and "`fix-pack-vol0.zip`" in files["vol0-sample.md"]
    assert "Expand-Archive -LiteralPath fix-pack.zip -DestinationPath fix-pack" in files["README-buyer.md"]
    assert "| `alpha` |" in files["README-buyer.md"] and "| `beta` |" in files["README-buyer.md"]


def test_the_starter_carries_no_template_word_outside_its_slots_and_no_private_name(world: dict) -> None:
    for name, text in stamp(world).items():
        bare = pb.SLOT_RE.sub("", text).lower()
        assert [t for t in pc.TEMPLATE_LEFT if t.lower() in bare] == [], name
        assert pc.PRIVATE.search(text) is None, name
        assert "\r" not in text, name


def test_pack_check_reports_only_the_open_slots_of_a_stamped_pack(world: dict) -> None:
    files = stamp(world)
    rep = check(world)
    found = fails(rep)
    assert sorted(w.split(":")[0] for w in found) == ["README-buyer.md", "listing.md", "price evidence", "vol0-sample.md"], found
    by_file = {w.split(":")[0]: w for w in found}
    for name in ("README-buyer.md", "listing.md", "vol0-sample.md"):
        assert f": {len(pb.open_slots(files[name]))} open slots to write (line " in by_file[name], by_file[name]
    assert by_file["price evidence"].startswith("price evidence: 0 https URLs"), "the evidence section holds only slots"
    needs = [w for lv, w in rep.lines if lv == "NEEDS"]
    assert len(needs) == 3 and all("needed: {{slot:" in w for w in needs)
    structural = ("missing", "price:", "Licences", "Proof", "Free sample", "template or draft", "AI disclosure", "pack.json", "stale", "private")
    assert not [w for w in found if any(s in w for s in structural)], found
    passes = [w for lv, w in rep.lines if lv == "PASS"]
    assert any(w.startswith("pack.json:") for w in passes) and any(w.startswith("price:") for w in passes)
    assert any("current" in w for w in passes), "the zips build from the starter README and are current"


def test_writing_every_slot_leaves_nothing_for_the_gate_but_the_store_assets(world: dict) -> None:
    files = stamp(world)
    pages = iter(["https://shop.example/one: a pack at $12", "https://shop.example/two: a pack at $20", "https://shop.example/three: a pack at $9"])
    for name, text in files.items():
        text = re.sub(r"\{\{slot: https URL of a seller page[^}]*\}\}", lambda m: next(pages), text) if name == "listing.md" else text
        (world["pack_dir"] / name).write_text(pb.SLOT_RE.sub("written text", text), encoding="utf-8", newline="\n")
    rep = check(world)
    assert fails(rep) == [], fails(rep)
    assert len([1 for lv, _ in rep.lines if lv == "NEEDS"]) == 3, "a store asset stays a request until its file exists"
    assert [w for lv, w in rep.lines if lv == "WARN"] == ["price evidence: 3 URLs not fetched (--offline)"]


@pytest.mark.parametrize("existing", list(pb.STARTER_FILES))
def test_it_refuses_to_overwrite_and_writes_none_of_the_four(world: dict, existing: str) -> None:
    (world["pack_dir"] / existing).write_text("mine\n", encoding="utf-8")
    with pytest.raises(ValueError, match="already has " + re.escape(existing)):
        pb.write_starters(world["pack_dir"], world["skills"])
    assert sorted(p.name for p in world["pack_dir"].iterdir()) == sorted([existing, "pack.json"])
    assert (world["pack_dir"] / existing).read_text(encoding="utf-8") == "mine\n"
    r = subprocess.run([sys.executable, str(g.ROOT / "tools" / "pack_build.py"), str(world["pack_dir"]), "--starter", "--skills", str(world["skills"])],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused: fix-pack already has"), r.stdout + r.stderr


def test_a_missing_or_unusable_pack_json_is_refused_with_nothing_written(world: dict) -> None:
    (world["pack_dir"] / "pack.json").unlink()
    with pytest.raises(ValueError, match="cannot read"):
        pb.write_starters(world["pack_dir"], world["skills"])
    (world["pack_dir"] / "pack.json").write_text(json.dumps({"slug": "fix-pack", "title": "T", "version": "1.0.0", "price_usd": 9, "skills": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="pack.json lacks"):
        pb.write_starters(world["pack_dir"], world["skills"])
    assert [p.name for p in world["pack_dir"].iterdir()] == ["pack.json"]


def test_the_command_line_writes_the_set_and_says_how_many_slots_are_open(world: dict) -> None:
    r = subprocess.run([sys.executable, str(g.ROOT / "tools" / "pack_build.py"), str(world["pack_dir"]), "--starter", "--skills", str(world["skills"])],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    assert [Path(ln[len("wrote "):]).name for ln in lines if ln.startswith("wrote ")] == list(pb.STARTER_FILES)
    total = sum(len(pb.open_slots((world["pack_dir"] / n).read_text(encoding="utf-8"))) for n in pb.STARTER_FILES)
    assert lines[-1].startswith(f"{total} open slots: write each one;") and total > 20
    assert not (world["root"] / "dist").exists(), "the starter builds nothing"


def test_the_real_pack_is_still_a_gate_clean_listing_of_the_same_shape() -> None:
    real = (REAL_PACK / "listing.md").read_text(encoding="utf-8")
    assert pb.open_slots(real) == []
    secs = pc.sections_of(real)
    assert [s for s in pc.SECTIONS if not any(k.startswith(s) for k in secs)] == []
    assert [f for f in pc.FIELDS if pc.field(real, f) is None] == []
