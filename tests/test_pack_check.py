"""pack_build and pack_check: the gate for a pack that is for sale, on fixture packs and on the real Fleet Vol 1."""
import json
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

sys.path.insert(0, str(g.ROOT / "tools"))
import pack_build as pb  # noqa: E402
import pack_check as pc  # noqa: E402

REAL_PACK = g.ROOT / "packs" / "fleet-vol-1"
GIF = b"GIF89a" + bytes(12_000)
PNG = b"\x89PNG\r\n\x1a\n" + bytes(8_000)

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


def set_listing(fix: dict, old: str, new: str) -> None:
    p = fix["pack_dir"] / "listing.md"
    assert old in p.read_text(encoding="utf-8"), old
    p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")


def set_pack(fix: dict, **changes) -> None:
    p = fix["pack_dir"] / "pack.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d.update(changes)
    p.write_text(json.dumps(d), encoding="utf-8")


def test_a_good_pack_passes_and_lists_the_assets_it_still_needs(fix: dict) -> None:
    rep = run(fix)
    assert fails(rep) == [], fails(rep)
    needs = [w for lv, w in rep.lines if lv == "NEEDS"]
    assert len(needs) == 3 and any("cover" in w for w in needs) and any("demo" in w for w in needs) and any("screenshots" in w for w in needs)
    audit, _ = pc.load_factory_audit(pc.find_factory_preflight())
    assert rep.count("WARN") == (1 if audit else 2)  # price evidence not fetched offline; factory gate warns when absent


def test_the_factory_buyer_gate_passes_a_good_pack_on_a_staged_product_layout(fix: dict) -> None:
    audit, reason = pc.load_factory_audit(pc.find_factory_preflight())
    if audit is None:
        pytest.skip(f"factory buyer-file gate unavailable: {reason}")
    rep = run(fix, factory_audit=audit)
    assert fails(rep) == [], fails(rep)
    assert any(w == "factory preflight: buyer-file gate PASS (JUDGE.md, listing/price.txt, one buyer zip)"
               for lv, w in rep.lines if lv == "PASS")


def test_factory_findings_become_pack_failures(fix: dict) -> None:
    rep = run(fix, factory_audit=lambda product: ["dist/: expected exactly one buyer zip, found 0"])
    assert any("factory preflight: dist/:" in w for w in fails(rep))


def test_an_unavailable_factory_gate_warns_instead_of_failing(fix: dict, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("FACTORY_PREFLIGHT", str(tmp_path / "nowhere.py"))
    rep = run(fix)
    assert fails(rep) == [] and any("buyer-file gate unavailable" in w for lv, w in rep.lines if lv == "WARN")


def test_the_buyer_zip_holds_the_skills_each_as_its_own_zip_and_a_manifest_with_sha256(fix: dict) -> None:
    with zipfile.ZipFile(fix["dist"] / "fix-pack.zip") as z:
        names = z.namelist()
        manifest = json.loads(z.read("manifest.json"))
    assert {"README.md", "LICENSES.md", "manifest.json", "skills/alpha/SKILL.md", "zips/alpha.zip", "proof/alpha-live-proof.json"} <= set(names)
    assert not any(n.startswith("skills/free-one") for n in names)
    assert not any(n.endswith("live-proof.json") and n.startswith("skills/") for n in names), "proofs are carried in proof/, not inside a skill folder"
    assert {r["path"] for r in manifest["files"]} == set(names) - {"manifest.json"}
    inner = pb.zipfile.ZipFile(__import__("io").BytesIO(zipfile.ZipFile(fix["dist"] / "fix-pack.zip").read("zips/beta.zip")))
    assert "SKILL.md" in inner.namelist() and "references/more.md" in inner.namelist()
    with zipfile.ZipFile(fix["dist"] / "fix-pack-vol0.zip") as z:
        assert "SKILL.md" in z.namelist() and "NOTICE.md" in z.namelist()


def test_the_build_is_reproducible(fix: dict, tmp_path: Path) -> None:
    again = tmp_path / "dist2"
    pb.build(fix["pack_dir"], again, fix["root"] / "skills")
    for name in ("fix-pack.zip", "fix-pack-vol0.zip"):
        assert (again / name).read_bytes() == (fix["dist"] / name).read_bytes()


def test_a_dist_folder_inside_skills_is_refused() -> None:
    r = subprocess.run([sys.executable, str(g.ROOT / "tools" / "pack_build.py"), str(REAL_PACK), "--dist", str(g.SKILLS / "x" / "out")],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 2 and "inside skills/" in r.stdout
    assert not (g.SKILLS / "x").exists()


def test_a_noncommercial_skill_is_never_in_a_priced_pack(fix: dict) -> None:
    d = json.loads((fix["pack_dir"] / "pack.json").read_text(encoding="utf-8"))
    d["skills"][0]["licence"] = "CC-BY-NC-SA-3.0"
    (fix["pack_dir"] / "pack.json").write_text(json.dumps(d), encoding="utf-8")
    assert any("NonCommercial skill is never in a priced pack" in w for w in fails(run(fix)))
    d["skills"][0]["licence"] = "MIT"
    (fix["pack_dir"] / "pack.json").write_text(json.dumps(d), encoding="utf-8")
    (fix["root"] / "skills" / "alpha" / "SKILL.md").write_text("---\nname: alpha\ndescription: Use when x.\nlicense: CC-BY-NC-SA-3.0 (derived)\n---\nbody\n", encoding="utf-8")
    assert any("NonCommercial source in a priced pack" in w for w in fails(run(fix)))


def test_a_licence_nobody_may_sell_under_fails(fix: dict) -> None:
    d = json.loads((fix["pack_dir"] / "pack.json").read_text(encoding="utf-8"))
    d["skills"][1]["licence"] = "All rights reserved"
    (fix["pack_dir"] / "pack.json").write_text(json.dumps(d), encoding="utf-8")
    assert any("not one of" in w for w in fails(run(fix)))


def test_the_vol0_skill_cannot_also_be_a_paid_skill(fix: dict) -> None:
    d = json.loads((fix["pack_dir"] / "pack.json").read_text(encoding="utf-8"))
    d["vol0"]["name"] = "alpha"
    (fix["pack_dir"] / "pack.json").write_text(json.dumps(d), encoding="utf-8")
    assert any("also in the paid skills" in w for w in fails(run(fix)))


def test_the_price_must_agree_in_listing_price_txt_and_pack_json(fix: dict) -> None:
    (fix["pack_dir"] / "price.txt").write_text("$12\n", encoding="utf-8")
    assert any(w.startswith("price:") and "must match" in w for w in fails(run(fix)))
    (fix["pack_dir"] / "price.txt").write_text("$9\n", encoding="utf-8")
    set_listing(fix, "Price: $9", "Price: free")
    assert any(w.startswith("price:") for w in fails(run(fix)))


@pytest.mark.parametrize("remove", ["Status", "AI disclosure", "Repository", "Weekly installs", "Sales"])
def test_a_missing_listing_field_fails(fix: dict, remove: str) -> None:
    text = (fix["pack_dir"] / "listing.md").read_text(encoding="utf-8")
    (fix["pack_dir"] / "listing.md").write_text("\n".join(ln for ln in text.splitlines() if not ln.startswith(remove + ":")), encoding="utf-8")
    assert any(f"field {remove}:" in w for w in fails(run(fix)))


def test_a_missing_section_and_template_text_fail(fix: dict) -> None:
    set_listing(fix, "## Install\n\nCopy the folders.\n", "")
    assert any("section ## install" in w for w in fails(run(fix)))
    set_listing(fix, "Node 24.", "Node 24. TODO write more. {{name}}")
    assert any("template or draft text left" in w for w in fails(run(fix)))


def test_the_ai_disclosure_must_say_what(fix: dict) -> None:
    set_listing(fix, "AI disclosure: generated: text written by an AI agent and checked by tests.", "AI disclosure: yes")
    assert any("AI disclosure" in w for w in fails(run(fix)))


def test_every_skill_must_be_named_with_its_licence_and_its_own_proof_line(fix: dict) -> None:
    set_listing(fix, "- `beta`: MIT and Apache-2.0.", "- `beta`: MIT.")
    assert any("'## Licences' must name beta" in w for w in fails(run(fix)))
    set_listing(fix, "- `beta`: MIT.", "- `beta`: MIT and Apache-2.0.")
    set_listing(fix, "- `alpha`: 2026-10-03, 3 passed.", "- `alpha`: 2026-10-03, 99 passed.")
    assert any("Proof' line for alpha must carry 2026-10-03 and '3 passed'" in w for w in fails(run(fix)))
    set_listing(fix, "- `alpha`: 2026-10-03, 99 passed.", "- `alpha`: 2026-10-03, 3 passed.")
    set_listing(fix, "- `beta`: does another.", "- another thing.")
    assert any("does not name beta" in w for w in fails(run(fix)))


def test_the_free_sample_section_must_name_the_vol0_skill_and_its_licence(fix: dict) -> None:
    set_listing(fix, "`free-one`, CC-BY-NC-SA-3.0, free.", "a free thing.")
    assert any("Free sample" in w for w in fails(run(fix)))


def test_a_private_path_or_another_repos_name_in_the_listing_fails(fix: dict) -> None:
    set_listing(fix, "Node 24.", "Node 24 at C:\\Users\\me\\Desktop\\x")
    assert any("private path" in w for w in fails(run(fix)))


def test_a_failing_skill_gate_fails_the_pack(fix: dict) -> None:
    rep = run(fix, skill_problems=lambda name: ["live proof: changed since its live tests last passed"] if name == "beta" else [])
    found = fails(rep)
    assert "skill beta: live proof: changed since its live tests last passed" in found
    audit, _ = pc.load_factory_audit(pc.find_factory_preflight())
    if audit is None:
        assert found == ["skill beta: live proof: changed since its live tests last passed"]
    else:
        assert any(w.startswith("factory preflight: independent JUDGE.md PASS is missing") for w in found), \
            "the staged verdict follows our own gate, so the buyer-file gate echoes a failing pack"


def test_a_skill_that_changed_after_the_zip_was_built_makes_the_zip_stale(fix: dict) -> None:
    (fix["root"] / "skills" / "alpha" / "references" / "more.md").write_text("changed\n", encoding="utf-8")
    assert any("is stale" in w and "skills/alpha/references/more.md" in w for w in fails(run(fix)))
    pb.build(fix["pack_dir"], fix["dist"], fix["root"] / "skills")
    assert fails(run(fix)) == []


def test_a_missing_or_extra_archive_fails(fix: dict) -> None:
    (fix["dist"] / "fix-pack-vol0.zip").unlink()
    assert any("fix-pack-vol0.zip is missing" in w for w in fails(run(fix)))
    pb.build(fix["pack_dir"], fix["dist"], fix["root"] / "skills")
    shutil.copy(fix["dist"] / "fix-pack.zip", fix["dist"] / "fix-pack-old.zip")
    assert any("unexpected archives ['fix-pack-old.zip']" in w for w in fails(run(fix)))


def _rewrite(fix: dict, edit) -> None:
    path = fix["dist"] / "fix-pack.zip"
    with zipfile.ZipFile(path) as z:
        members = {n: z.read(n) for n in z.namelist()}
    edit(members)
    with zipfile.ZipFile(path, "w") as z:
        for n, d in members.items():
            z.writestr(n, d)


def test_junk_unsafe_paths_and_a_wrong_manifest_in_the_zip_fail(fix: dict) -> None:
    _rewrite(fix, lambda m: m.update({"skills/alpha/__pycache__/x.pyc": b"x", "../escape.txt": b"x"}))
    found = " ".join(fails(run(fix)))
    assert "junk files" in found and "unsafe paths" in found
    pb.build(fix["pack_dir"], fix["dist"], fix["root"] / "skills")
    _rewrite(fix, lambda m: m.update({"README.md": b"# edited after the manifest\n"}))
    assert any("size or sha256 of README.md is wrong" in w for w in fails(run(fix)))


def test_the_free_skill_inside_the_paid_zip_fails(fix: dict) -> None:
    _rewrite(fix, lambda m: m.update({"skills/free-one/SKILL.md": b"---\nname: free-one\nlicense: CC-BY-NC-SA-3.0\n---\n"}))
    found = " ".join(fails(run(fix)))
    assert "free Vol 0 skill free-one is inside the paid zip" in found and "NonCommercial licence" in found


def test_a_skill_that_names_a_file_the_zip_does_not_hold_fails(fix: dict) -> None:
    skill = fix["root"] / "skills" / "alpha" / "SKILL.md"
    skill.write_text(skill.read_text(encoding="utf-8") + "\nAlso `scripts/missing.py`.\n", encoding="utf-8")
    pb.build(fix["pack_dir"], fix["dist"], fix["root"] / "skills")
    assert any("names scripts/missing.py, which is not in the zip" in w for w in fails(run(fix)))


def test_a_private_path_inside_a_skill_in_the_zip_fails(fix: dict) -> None:
    skill = fix["root"] / "skills" / "alpha" / "references" / "more.md"
    skill.write_text("see C:/Users/me/Desktop/x\n", encoding="utf-8")
    pb.build(fix["pack_dir"], fix["dist"], fix["root"] / "skills")
    assert any("private path or another repo's name in ['skills/alpha/references/more.md'" in w for w in fails(run(fix)))


def test_price_evidence_needs_three_pages_and_a_gone_page_fails(fix: dict) -> None:
    ok = run(fix, offline=False, fetch=lambda url: 200)
    assert fails(ok) == [] and ok.count("WARN") == 0
    gone = run(fix, offline=False, fetch=lambda url: 404 if url.endswith("two") else 200)
    assert any("page gone" in w and "shop.example/two" in w for w in fails(gone))
    quiet = run(fix, offline=False, fetch=lambda url: 0)
    assert fails(quiet) == [] and any("no clean answer" in w for lv, w in quiet.lines if lv == "WARN")
    set_listing(fix, "- https://shop.example/three: costs $9.\n", "")
    assert any("2 https URLs" in w for w in fails(run(fix)))


def test_store_assets_present_must_be_real_files_of_enough_size(fix: dict) -> None:
    assets = fix["pack_dir"] / "assets"
    assets.mkdir()
    (assets / "cover.png").write_bytes(PNG)
    (assets / "demo.gif").write_bytes(GIF)
    (assets / "s1.png").write_bytes(PNG)
    (assets / "s2.png").write_bytes(PNG)
    set_listing(fix, "- cover: needed: a PNG cover.", "- cover: assets/cover.png")
    set_listing(fix, "- demo: needed: a GIF of the session.", "- demo: assets/demo.gif")
    set_listing(fix, "- screenshots: needed: three PNG captures.", "- screenshots: assets/s1.png, assets/s2.png")
    rep = run(fix)
    assert fails(rep) == [] and rep.count("NEEDS") == 0
    (assets / "demo.gif").write_bytes(b"GIF89a" + bytes(40))  # a 46-byte placeholder is not a demo
    assert any("demo" in w and "bytes, want 10000+" in w for w in fails(run(fix)))
    (assets / "demo.gif").write_bytes(b"not an image" + bytes(20_000))
    assert any("is not a PNG, GIF or JPEG" in w for w in fails(run(fix)))
    (assets / "demo.gif").unlink()
    assert any("demo.gif does not exist" in w for w in fails(run(fix)))


def test_a_listing_must_say_something_about_every_asset(fix: dict) -> None:
    set_listing(fix, "- demo: needed: a GIF of the session.\n", "")
    assert any("says nothing about demo" in w for w in fails(run(fix)))


def test_with_a_live_listing_line_every_needed_asset_is_a_failure(fix: dict) -> None:
    with (fix["pack_dir"] / "listing.md").open("a", encoding="utf-8") as fh:
        fh.write("\nLive listing: https://store.example/fix-pack\n")
    rep = run(fix)
    assert rep.count("NEEDS") == 0
    assert sum("store assets:" in w for w in fails(rep)) == 3


def test_the_command_line_ends_with_one_result_line_and_the_exit_code_follows(fix: dict, tmp_path: Path) -> None:
    r = subprocess.run([sys.executable, str(g.ROOT / "tools" / "pack_check.py"), str(tmp_path / "nowhere")], capture_output=True, text=True,
                       stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 1 and r.stdout.strip() == f"RESULT FAIL: {tmp_path / 'nowhere'} is not a folder"


def test_the_real_pack_files_match_what_the_listing_says() -> None:
    pack = json.loads((REAL_PACK / "pack.json").read_text(encoding="utf-8"))
    assert pack["slug"] == "fleet-vol-1" and [s["name"] for s in pack["skills"]] == ["pwsh-for-bash-writers", "real-browser-automation", "bevy-rust-ecs"]
    assert pack["vol0"]["name"] == "git-one-branch" and "NC" in pack["vol0"]["licence"]
    listing = (REAL_PACK / "listing.md").read_text(encoding="utf-8")
    pairs = json.loads((g.SKILLS / "pwsh-for-bash-writers" / "references" / "pairs.json").read_text(encoding="utf-8"))["pairs"]
    md_pairs = len(re.findall(r"(?m)^### ", (g.SKILLS / "pwsh-for-bash-writers" / "references" / "pairs.md").read_text(encoding="utf-8")))
    assert len(pairs) == md_pairs == 49
    assert "49 bash-to-pwsh pairs" in listing and "49 habits" in (REAL_PACK / "README-buyer.md").read_text(encoding="utf-8")
    assert not pc.LIVE.search(listing), "going live is the store's step: nobody adds the Live listing line before a page exists"
    assert (g.SKILLS / "real-browser-automation" / "scripts" / "cdp.mjs").stat().st_size // 1000 == 30 and "30 KB" in listing
    assert f"${pack['price_usd']:g}" in (REAL_PACK / "price.txt").read_text(encoding="utf-8")


@live
def test_the_real_pack_passes_the_gate_and_the_readme_install_commands_work(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    pb.build(REAL_PACK, dist)
    r = subprocess.run([sys.executable, str(g.ROOT / "tools" / "pack_check.py"), str(REAL_PACK), "--dist", str(dist), "--offline"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
    assert r.returncode == 0, r.stdout + r.stderr
    last = r.stdout.strip().splitlines()[-1]
    assert last.startswith("RESULT PASS: fleet-vol-1") and "3 store assets still needed" in last, last
    # the PowerShell block of the README, run against the real zip with a scratch folder as the skills folder
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh 7 is not installed")
    readme = (REAL_PACK / "README-buyer.md").read_text(encoding="utf-8")
    block = re.search(r"```powershell\n(.*?)```", readme, re.S).group(1)
    assert "$HOME\\.claude\\skills" in block
    skills_dest = tmp_path / "claude home" / "skills"
    script = block.replace('"$HOME\\.claude\\skills"', f'"{skills_dest}"')
    shutil.copy(dist / "fleet-vol-1.zip", tmp_path / "fleet-vol-1.zip")
    p = subprocess.run([pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", script], cwd=tmp_path, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=180)
    assert p.returncode == 0, p.stdout + p.stderr
    for name in ("pwsh-for-bash-writers", "real-browser-automation", "bevy-rust-ecs"):
        assert (skills_dest / name / "SKILL.md").is_file(), name
        assert re.search(rf"(?m)^name: {name}$", (skills_dest / name / "SKILL.md").read_text(encoding="utf-8"))
    assert not (skills_dest / "git-one-branch").exists()
