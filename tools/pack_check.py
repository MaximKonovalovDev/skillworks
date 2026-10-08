"""Pack gate: python tools/pack_check.py packs/<slug> [--dist DIR] [--offline]

Checks that a pack for sale is tested, honest and complete, short of going live. Prints one line per check
(`PASS`, `FAIL`, `WARN`, `NEEDS`) and ends with one `RESULT PASS` or `RESULT FAIL` line; exit 0 only on PASS.

FAIL means the pack must not be listed. NEEDS means a store asset (cover, demo, screenshots) is not made yet: it is
written down in the listing with its request and does not fail the pack, until a `Live listing:` line exists. Then every
NEEDS is a FAIL, because a live page must have its assets. WARN is a check that could not run (no network).

What it checks (the buyer-file gate of the factory, the publish-readiness gate of ClawHub, ours):
  pack.json            slug, semver, price, licences; a NonCommercial skill is never in a priced pack
  skills               each paid skill: format, eval gate, no scaffold text, live proof current
  listing.md           required fields and sections, every skill named with its licence, proof lines equal live-proof.json,
                       price equal to price.txt and pack.json, AI disclosure, no template text, no private paths,
                       no open `{{slot: ...}}` of the starter `pack_build.py --starter` writes (README-buyer.md and
                       vol0-sample.md are checked for open slots too)
  dist/<slug>.zip      current (rebuilt in memory and compared), safe paths, no junk, manifest sha256 matches, each skill
                       also as zips/<name>.zip with SKILL.md at the root, every file a SKILL.md names is inside
  dist/<slug>-vol0.zip the free skill with SKILL.md at the root and its licence notice; never inside the paid zip
  price evidence       3 or more https URLs; 404 or 410 fails, no network warns
  store assets         cover, demo, screenshots: present and big enough, or `needed:` with the request
  factory preflight    the factory buyer-file gate audit() run read-only on a staged factory-layout copy
                       (listing/itch.md, listing/price.txt, one buyer zip in dist/, JUDGE.md with our own verdict);
                       each of its findings is a FAIL. --no-factory skips it.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import re
import shutil
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path
from typing import Callable

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import pack_build  # noqa: E402

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
PRICE = re.compile(r"\$\s*(\d+(?:\.\d{1,2})?)")
LIVE = re.compile(r"(?m)^Live listing:\s*(https://\S+)\s*$")
URL = re.compile(r"https://[^\s)>\]`]+")
NC = re.compile(r"NonCommercial|\bNC\b|-NC-", re.I)
SELLABLE = ("MIT", "Apache-2.0", "BSD-3-Clause", "BSD-2-Clause", "CC-BY-4.0", "ISC", "CC0")
TEMPLATE_LEFT = ("{{", "}}", "<what>", "$X.00", "TODO", "TBD", "lorem ipsum", "one line, 60-110 characters")
PRIVATE = re.compile(r"Users[\\/]me\b|Desktop[\\/]|[A-Za-z]:[\\/]empire\b|engine2040|autonomous-factory|fp-research|marketing-studio|jobhunt|design-studio|forge-data|\.empire", re.I)
JUNK = re.compile(r"(^|/)(\.DS_Store|Thumbs\.db|__pycache__|node_modules|\.git|\.env)(/|$)|\.(pyc|log|tmp|bak)$", re.I)
SECTIONS = pack_build.REQUIRED_SECTIONS  # one list of headings and fields: tools/pack_build.py writes the starter from the same constants
FIELDS = pack_build.LISTING_FIELDS
ASSET_KINDS = {"cover": 5_000, "demo": 10_000, "screenshots": 5_000}
IMAGE_MAGIC = (b"\x89PNG\r\n\x1a\n", b"GIF87a", b"GIF89a", b"\xff\xd8\xff")


class Report:
    def __init__(self) -> None:
        self.lines: list[tuple[str, str]] = []

    def add(self, level: str, what: str) -> None:
        self.lines.append((level, what))

    def ok(self, what: str) -> None:
        self.add("PASS", what)

    def count(self, level: str) -> int:
        return sum(1 for lv, _ in self.lines if lv == level)


def default_skill_problems(name: str) -> list[str]:
    """The fleet gates of tests/skill_gates.py for one skill: format, eval gate, live proof current, no scaffold text."""
    sys.path[:0] = [str(ROOT / "tests"), str(ROOT)]
    import skill_gates as g
    from book2skill import build as build_mod

    problems = []
    for label, fn in (("format", g.check_format), ("eval gate", g.check_eval), ("live proof", g.check_proof)):
        try:
            with contextlib.redirect_stdout(io.StringIO()):  # audit and eval print their own JSON reports
                fn(name)
        except (AssertionError, OSError, ValueError) as err:
            problems.append(f"{label}: {err}")
    left = build_mod.scaffold_leftovers(g.SKILLS / name)
    if left:
        problems.append("scaffold text left in " + ", ".join(left))
    return problems


def fetch_status(url: str) -> int:
    """HTTP status of a page (GET, 15 s); 0 when the network gave no answer."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (pack_check)"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return resp.status
    except urllib.error.HTTPError as err:
        return err.code
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0


def sections_of(text: str) -> dict[str, str]:
    parts = re.split(r"(?m)^##\s+", text)
    return {p.split("\n", 1)[0].strip().lower(): p.split("\n", 1)[1] if "\n" in p else "" for p in parts[1:]}


def field(text: str, key: str) -> str | None:
    m = re.search(rf"(?im)^[\s>*-]*{re.escape(key)}\s*:\s*(.+?)\s*$", text)
    return m.group(1) if m else None


def check_manifest(pack_dir: Path, rep: Report) -> dict | None:
    try:
        pack = json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))
    except (OSError, ValueError) as err:
        rep.add("FAIL", f"pack.json: cannot read ({err})")
        return None
    bad = []
    if pack.get("slug") != pack_dir.name:
        bad.append(f"slug {pack.get('slug')!r} is not the folder name {pack_dir.name!r}")
    if not SEMVER.match(str(pack.get("version", ""))):
        bad.append("version is not semver (1.2.3)")
    if not isinstance(pack.get("price_usd"), (int, float)) or pack["price_usd"] <= 0:
        bad.append("price_usd must be a number above 0 for a pack for sale")
    if not pack.get("skills"):
        bad.append("no skills")
    for s in pack.get("skills", []):
        for key in ("name", "licence", "credit"):
            if not s.get(key):
                bad.append(f"skill {s.get('name', '?')} has no {key}")
        if NC.search(s.get("licence", "")):
            bad.append(f"{s.get('name')} is {s['licence']}: a NonCommercial skill is never in a priced pack")
        elif not any(tok in s.get("licence", "") for tok in SELLABLE):
            bad.append(f"{s.get('name')} licence {s.get('licence')!r} is not one of {', '.join(SELLABLE)}")
    vol0 = pack.get("vol0") or {}
    if not vol0.get("name") or not vol0.get("licence") or not vol0.get("credit"):
        bad.append("vol0 needs name, licence and credit (the free sample skill)")
    elif vol0["name"] in [s.get("name") for s in pack.get("skills", [])]:
        bad.append("the Vol 0 skill is also in the paid skills")
    if bad:
        for b in bad:
            rep.add("FAIL", f"pack.json: {b}")
        return None
    rep.ok(f"pack.json: {pack['slug']} {pack['version']}, ${pack['price_usd']:g}, {len(pack['skills'])} skills, every licence sellable")
    return pack


def check_skills(pack: dict, skills: Path, rep: Report, skill_problems: Callable[[str], list[str]]) -> None:
    for s in pack["skills"]:
        name = s["name"]
        if not (skills / name / "SKILL.md").is_file():
            rep.add("FAIL", f"skill {name}: skills/{name}/SKILL.md is missing")
            continue
        text = (skills / name / "SKILL.md").read_text(encoding="utf-8")
        m = re.search(r"(?m)^license:\s*(.+)$", text)
        if m and NC.search(m.group(1)):
            rep.add("FAIL", f"skill {name}: SKILL.md says {m.group(1).strip()}, a NonCommercial source in a priced pack")
        problems = skill_problems(name)
        if problems:
            for p in problems:
                rep.add("FAIL", f"skill {name}: {p}")
        else:
            rep.ok(f"skill {name}: format, eval gate, live proof current, no scaffold text")


def slot_finding(name: str, slots: list[tuple[int, str]]) -> str:
    """One finding for the `{{slot: ...}}` lines of a starter that are still open: how many, and the first few."""
    shown = "; ".join(f"line {n}: {what[:48]}" for n, what in slots[:3])
    return f"{name}: {len(slots)} open slots to write ({shown}{'; ...' if len(slots) > 3 else ''})"


def check_buyer_files(pack_dir: Path, rep: Report) -> None:
    """The README that ships in the zip and the Vol 0 page must carry no open slot of a starter."""
    for name in ("README-buyer.md", "vol0-sample.md"):
        try:
            slots = pack_build.open_slots((pack_dir / name).read_text(encoding="utf-8"))
        except OSError:
            continue
        if slots:
            rep.add("FAIL", slot_finding(name, slots))


def check_listing(pack_dir: Path, pack: dict, skills: Path, rep: Report) -> tuple[str, bool]:
    path = pack_dir / "listing.md"
    if not path.is_file():
        rep.add("FAIL", "listing.md is missing")
        return "", False
    text = path.read_text(encoding="utf-8")
    live = bool(LIVE.search(text))
    missing = [f for f in FIELDS if field(text, f) is None]
    secs = sections_of(text)
    missing_sections = [s for s in SECTIONS if not any(k.startswith(s) for k in secs)]
    if missing or missing_sections:
        rep.add("FAIL", "listing.md: missing " + ", ".join([*(f"field {f}:" for f in missing), *(f"section ## {s}" for s in missing_sections)]))
    slots = pack_build.open_slots(text)
    if slots:
        rep.add("FAIL", slot_finding("listing.md", slots))
    bare = pack_build.SLOT_RE.sub("", text).lower()  # slots are reported above; the template words are looked for around them
    left = [t for t in TEMPLATE_LEFT if t.lower() in bare]
    if left:
        rep.add("FAIL", f"listing.md: template or draft text left ({', '.join(left)})")
    stated = field(text, "Price")
    price = PRICE.search(stated or "")
    price_txt = pack_dir / "price.txt"
    canon = PRICE.search(price_txt.read_text(encoding="utf-8")) if price_txt.is_file() else None
    if not price or float(price[1]) != float(pack["price_usd"]) or not canon or float(canon[1]) != float(pack["price_usd"]):
        rep.add("FAIL", f"price: listing says {stated!r}, price.txt says {canon[0] if canon else 'nothing'}, pack.json says ${pack['price_usd']:g}; all three must match")
    else:
        rep.ok(f"price: ${pack['price_usd']:g} in listing.md, price.txt and pack.json")
    disclosure = field(text, "AI disclosure") or ""
    if not re.match(r"(none|assisted|generated)\b", disclosure, re.I) or len(disclosure) < 12:
        rep.add("FAIL", "listing.md: 'AI disclosure:' must start with none, assisted or generated and say what")
    inside, lic, proof = (next((v for k, v in secs.items() if k.startswith(p)), "") for p in ("what is inside", "licences", "proof"))
    for s in pack["skills"]:
        name = s["name"]
        if name not in inside:
            rep.add("FAIL", f"listing.md: '## What is inside' does not name {name}")
        if name not in lic or s["licence"] not in lic:
            rep.add("FAIL", f"listing.md: '## Licences' must name {name} with its licence {s['licence']!r}")
        pf = skills / name / "references" / "live-proof.json"
        try:
            data = json.loads(pf.read_text(encoding="utf-8"))
            line = next((ln for ln in proof.splitlines() if name in ln), "")
            want = (data["date"][:10], re.match(r"\d+ passed", data["result"]).group(0))
            if not all(w in line for w in want):
                rep.add("FAIL", f"listing.md: '## Proof' line for {name} must carry {want[0]} and '{want[1]}' from its live-proof.json")
        except (OSError, ValueError, KeyError, AttributeError):
            rep.add("FAIL", f"listing.md: no readable live-proof.json for {name} to match the Proof line against")
    vol0 = pack["vol0"]["name"]
    if vol0 not in "\n".join(secs.get(k, "") for k in secs if k.startswith("free sample")) or pack["vol0"]["licence"] not in text:
        rep.add("FAIL", f"listing.md: '## Free sample' must name {vol0} and say {pack['vol0']['licence']}")
    if PRIVATE.search(text):
        rep.add("FAIL", f"listing.md: private path or another repo's name ({PRIVATE.search(text).group(0)})")
    if not any(lv == "FAIL" for lv, w in rep.lines if w.startswith(("listing.md", "price"))):
        rep.ok("listing.md: fields, sections, licences, proof lines, AI disclosure; no template text, no private names")
    return text, live


def check_evidence(listing: str, rep: Report, offline: bool, fetch: Callable[[str], int]) -> None:
    section = next((v for k, v in sections_of(listing).items() if k.startswith("price evidence")), "")
    urls = sorted(set(u.rstrip(".,;:") for u in URL.findall(section)))
    if len(urls) < 3:
        rep.add("FAIL", f"price evidence: {len(urls)} https URLs of sellers' own pages, want 3 or more")
        return
    gone, quiet = [], []
    for u in ([] if offline else urls):
        code = fetch(u)
        if code in (404, 410):
            gone.append(f"{u} ({code})")
        elif not 200 <= code < 400:
            quiet.append(f"{u} ({code or 'no answer'})")
    if gone:
        rep.add("FAIL", "price evidence: page gone: " + ", ".join(gone))
    elif offline:
        rep.add("WARN", f"price evidence: {len(urls)} URLs not fetched (--offline)")
    elif quiet:
        rep.add("WARN", "price evidence: no clean answer from " + ", ".join(quiet))
    else:
        rep.ok(f"price evidence: {len(urls)} seller pages answer")


def zip_problems(source: "Path | bytes") -> tuple[list[str], dict[str, bytes]]:
    problems, members = [], {}
    try:
        with zipfile.ZipFile(io.BytesIO(source) if isinstance(source, bytes) else source) as z:
            infos = [i for i in z.infolist() if not i.is_dir()]
            names = [i.filename.replace("\\", "/") for i in infos]
            if not names:
                problems.append("archive has no files")
            dup = sorted({n for n in names if names.count(n) > 1})
            if dup:
                problems.append(f"duplicate paths {dup[:3]}")
            unsafe = [n for n in names if n.startswith("/") or re.match(r"^[A-Za-z]:", n) or any(p in ("", "..") for p in n.split("/"))]
            if unsafe:
                problems.append(f"unsafe paths {unsafe[:3]}")
            junk = [n for n in names if JUNK.search(n)]
            if junk:
                problems.append(f"junk files {junk[:3]}")
            long = [n for n in names if len(n) > 150]
            if long:
                problems.append(f"paths over 150 characters {long[:2]}")
            bad = z.testzip()
            if bad:
                problems.append(f"corrupt member {bad}")
            for i, n in zip(infos, names):
                members[n] = z.read(i)
    except (OSError, zipfile.BadZipFile) as err:
        problems.append(f"cannot read ({err})")
    return problems, members


def differs(actual: dict[str, bytes], expected: dict[str, bytes]) -> str:
    """What differs between a zip's members and a fresh build, by content. A zip inside a zip is compared by its own
    members, because the compressed bytes depend on the zlib version of the machine that built it."""
    gone, extra = sorted(set(expected) - set(actual)), sorted(set(actual) - set(expected))
    changed = []
    for name in sorted(set(actual) & set(expected)):
        a, e = actual[name], expected[name]
        same = zip_problems(a)[1] == zip_problems(e)[1] if name.endswith(".zip") else a == e
        if not same:
            changed.append(name)
    return "; ".join(x for x in (f"missing {gone[:3]}" if gone else "", f"extra {extra[:3]}" if extra else "", f"changed {changed[:3]}" if changed else "") if x)


def referenced_files(skill_md: str) -> set[str]:
    return set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", skill_md))


def check_zips(pack_dir: Path, pack: dict, skills: Path, dist: Path, rep: Report) -> None:
    slug = pack["slug"]
    paid, free = dist / f"{slug}.zip", dist / f"{slug}-vol0.zip"
    strays = sorted(p.name for p in dist.glob(f"{slug}*.zip") if p not in (paid, free)) if dist.is_dir() else []
    if strays:
        rep.add("FAIL", f"dist: unexpected archives {strays}; the pack is exactly {paid.name} and {free.name}")
    for p in (paid, free):
        if not p.is_file():
            rep.add("FAIL", f"dist: {p.name} is missing (python tools/pack_build.py {pack_dir.as_posix()})")
    if not paid.is_file() or not free.is_file():
        return
    problems, members = zip_problems(paid)
    if len(paid.read_bytes()) > pack_build.MAX_BUNDLE_BYTES:
        problems.append("bundle over the size cap")
    for need in ("README.md", "LICENSES.md", "manifest.json"):
        if need not in members:
            problems.append(f"{need} missing")
    for s in pack["skills"]:
        name = s["name"]
        sm = members.get(f"skills/{name}/SKILL.md")
        if sm is None:
            problems.append(f"skills/{name}/SKILL.md missing")
            continue
        text = sm.decode("utf-8", "replace")
        if not re.search(rf"(?m)^name:\s*{re.escape(name)}\s*$", text):
            problems.append(f"skills/{name}/SKILL.md: frontmatter name is not {name}")
        for ref in sorted(referenced_files(text)):
            if f"skills/{name}/{ref}" not in members:
                problems.append(f"skills/{name}/SKILL.md names {ref}, which is not in the zip")
        inner = members.get(f"zips/{name}.zip")
        if inner is None:
            problems.append(f"zips/{name}.zip missing")
        else:
            ip, im = zip_problems(inner)
            problems += [f"zips/{name}.zip: {x}" for x in ip]
            if "SKILL.md" not in im:
                problems.append(f"zips/{name}.zip: SKILL.md is not at the root")
        if f"proof/{name}-live-proof.json" not in members:
            problems.append(f"proof/{name}-live-proof.json missing")
    vol0 = pack["vol0"]["name"]
    if any(n.startswith(f"skills/{vol0}/") or f"zips/{vol0}" in n for n in members):
        problems.append(f"the free Vol 0 skill {vol0} is inside the paid zip")
    if any(NC.search(m.decode("utf-8", "replace").split("---", 2)[1]) for n, m in members.items() if n.endswith("/SKILL.md") and m.count(b"---") >= 2):
        problems.append("a SKILL.md in the paid zip carries a NonCommercial licence")
    try:
        manifest = json.loads(members["manifest.json"])
        listed = {r["path"]: r for r in manifest["files"]}
        others = {n: d for n, d in members.items() if n != "manifest.json"}
        if set(listed) != set(others):
            problems.append(f"manifest.json and the zip list different files ({sorted(set(listed) ^ set(others))[:3]})")
        for n, d in others.items():
            r = listed.get(n)
            if r and (r["size"] != len(d) or r["sha256"] != hashlib.sha256(d).hexdigest()):
                problems.append(f"manifest.json: size or sha256 of {n} is wrong")
        if manifest.get("version") != pack["version"]:
            problems.append("manifest.json version differs from pack.json")
    except (KeyError, ValueError, TypeError):
        problems.append("manifest.json unreadable")
    leaked = [n for n, d in members.items() if n.endswith((".md", ".json", ".mjs", ".py", ".txt")) and PRIVATE.search(d.decode("utf-8", "replace"))]
    if leaked:
        problems.append(f"private path or another repo's name in {leaked[:3]}")
    stale = differs({n: d for n, d in members.items() if n != "manifest.json"}, pack_build.pack_files(pack_dir, pack, skills))
    if stale:
        problems.append(f"the file is stale ({stale}): the skills, README-buyer.md or pack.json changed since it was built (python tools/pack_build.py)")
    if problems:
        for pr in problems:
            rep.add("FAIL", f"{paid.name}: {pr}")
    else:
        rep.ok(f"{paid.name}: current, {len(members)} files, safe paths, manifest sha256 matches, each skill also as its own zip with SKILL.md at the root")
    fp, fm = zip_problems(free)
    fp += [] if "SKILL.md" in fm else ["SKILL.md is not at the root"]
    if "NOTICE.md" not in fm or pack["vol0"]["licence"] not in fm.get("NOTICE.md", b"").decode("utf-8", "replace"):
        fp.append("NOTICE.md with the licence is missing")
    stale = differs(fm, zip_problems(pack_build.build_vol0_zip(pack, skills))[1])
    if stale:
        fp.append(f"the file is stale ({stale}); python tools/pack_build.py")
    if fp:
        for pr in fp:
            rep.add("FAIL", f"{free.name}: {pr}")
    else:
        rep.ok(f"{free.name}: {vol0} with SKILL.md at the root and its licence notice")


def check_assets(pack_dir: Path, listing: str, live: bool, rep: Report) -> None:
    section = next((v for k, v in sections_of(listing).items() if k.startswith("store assets")), "")
    declared: dict[str, str] = {}
    for m in re.finditer(r"(?im)^\s*[-*]\s*(cover|demo|screenshots)\s*:\s*(.+?)\s*$", section):
        declared[m.group(1).lower()] = m.group(2)
    for kind, floor in ASSET_KINDS.items():
        what = declared.get(kind)
        if what is None:
            rep.add("FAIL", f"store assets: '## Store assets' says nothing about {kind} (write `- {kind}: needed: <request>` or the file path)")
        elif what.lower().startswith("needed"):
            rep.add("FAIL" if live else "NEEDS", f"store assets: {kind} {what}")
        else:
            bad = []
            for rel in [x.strip().strip("`") for x in what.split(",")]:
                f = pack_dir / rel
                if not f.is_file():
                    bad.append(f"{rel} does not exist")
                elif f.stat().st_size < floor:
                    bad.append(f"{rel} is {f.stat().st_size} bytes, want {floor}+")
                elif not any(f.read_bytes()[:12].startswith(mg) for mg in IMAGE_MAGIC) and not rel.lower().endswith((".mp4", ".webm")):
                    bad.append(f"{rel} is not a PNG, GIF or JPEG")
            if bad:
                rep.add("FAIL", f"store assets: {kind}: " + "; ".join(bad))
            else:
                rep.ok(f"store assets: {kind} present ({what})")


FACTORY_DIMS = ("value vs bar", "works out of the box", "preview sells it", "license clean", "listing-ready")


def find_factory_preflight() -> Path:
    """The factory buyer-file gate script, read-only. FACTORY_PREFLIGHT wins; else the sibling checkout next to
    this repo (same pattern as the EMPIRE_JSON default in tools/adopted_after.py)."""
    given = os.environ.get("FACTORY_PREFLIGHT")
    if given:
        return Path(given)
    return ROOT.parent / "autonomous-factory" / "engine" / "publish_preflight.py"


def load_factory_audit(path: Path) -> tuple[Callable | None, str]:
    """Import audit() from the factory gate without running its CLI (its main() only accepts folders under the
    factory products/ tree, so a staged copy is audited instead). Returns (audit, reason)."""
    if not path.is_file():
        return None, f"not found at {path.name}; set FACTORY_PREFLIGHT to the engine script"
    engine_dir = str(path.parent)
    sys.path.insert(0, engine_dir)  # the script does `import verdict` from its own folder
    try:
        spec = importlib.util.spec_from_file_location("skillworks_factory_preflight", str(path))
        if spec is None or spec.loader is None:
            return None, f"cannot load {path.name}"
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        audit = getattr(mod, "audit", None)
        if not callable(audit):
            return None, f"{path.name} has no audit()"
        return audit, ""
    except Exception as err:  # noqa: BLE001 - a foreign traceback must not break our gate
        return None, f"cannot import {path.name} ({err})"
    finally:
        with contextlib.suppress(ValueError):
            sys.path.remove(engine_dir)


def judge_text(slug: str, ok: bool) -> str:
    """Our own verdict sheet for the staged copy: the factory judge_gate() needs VERDICT in the first five lines
    plus all five /10 dims, so the sheet carries our own gate outcome honestly (PASS only when our checks passed)."""
    verdict, score = ("PASS", "10/10") if ok else ("FAIL", "0/10")
    lines = [f"# Pack judge: {slug}", f"VERDICT: {verdict}",
             f"tools/pack_check.py own checks {'passed' if ok else 'failed'}; scored here for the buyer-file gate.",
             "", "Scores:"]
    lines += [f"- {dim}: {score}" for dim in FACTORY_DIMS]
    return "\n".join(lines) + "\n"


def stage_factory_product(pack_dir: Path, pack: dict, dist: Path, tmp: Path, own_ok: bool) -> Path:
    """A scratch copy laid out like a factory product: listing/itch.md plus listing/price.txt, exactly one buyer
    zip in dist/, JUDGE.md with our own verdict. Written to tmp (never committed), read back by audit()."""
    product = tmp / pack["slug"]
    shutil.rmtree(product, ignore_errors=True)
    (product / "listing").mkdir(parents=True)
    (product / "dist").mkdir(parents=True)
    (product / "listing" / "itch.md").write_text((pack_dir / "listing.md").read_text(encoding="utf-8"), encoding="utf-8")
    shutil.copy2(pack_dir / "price.txt", product / "listing" / "price.txt")
    paid = dist / f"{pack['slug']}.zip"
    shutil.copy2(paid, product / "dist" / paid.name)
    (product / "JUDGE.md").write_text(judge_text(pack["slug"], own_ok), encoding="utf-8")
    return product


def check_factory_preflight(pack_dir: Path, pack: dict, dist: Path, rep: Report, *,
                            enabled: bool = True, audit: Callable | None = None) -> None:
    """Run the factory buyer-file gate audit() on the staged copy; each of its findings is a FAIL. When the gate
    script is not on this machine the gate warns instead of failing, so the pack still stands on our own checks."""
    if not enabled:
        return
    if audit is None:
        audit, reason = load_factory_audit(find_factory_preflight())
        if audit is None:
            rep.add("WARN", f"factory preflight: buyer-file gate unavailable ({reason}); own checks only")
            return
    if not (dist / f"{pack['slug']}.zip").is_file():
        return  # check_zips already recorded the missing buyer file
    with tempfile.TemporaryDirectory(prefix="pack-factory-") as tmp:
        product = stage_factory_product(pack_dir, pack, dist, Path(tmp), rep.count("FAIL") == 0)
        try:
            findings = audit(product)
        except Exception as err:  # noqa: BLE001 - see load_factory_audit
            rep.add("FAIL", f"factory preflight: audit() raised ({err})")
            return
    if findings:
        for finding in findings:
            rep.add("FAIL", f"factory preflight: {finding}")
    else:
        rep.ok("factory preflight: buyer-file gate PASS (JUDGE.md, listing/price.txt, one buyer zip)")


def check_pack(pack_dir: Path, *, root: Path = ROOT, dist: Path | None = None, offline: bool = False,
               skill_problems: Callable[[str], list[str]] = default_skill_problems,
               fetch: Callable[[str], int] = fetch_status,
               factory: bool = True, factory_audit: Callable | None = None) -> Report:
    rep = Report()
    pack = check_manifest(pack_dir, rep)
    if pack is None:
        return rep
    skills = root / "skills"
    check_skills(pack, skills, rep, skill_problems)
    listing, live = check_listing(pack_dir, pack, skills, rep)
    check_buyer_files(pack_dir, rep)
    if listing:
        check_evidence(listing, rep, offline, fetch)
        check_assets(pack_dir, listing, live, rep)
    resolved = dist or root / "dist"
    check_zips(pack_dir, pack, skills, resolved, rep)
    check_factory_preflight(pack_dir, pack, resolved, rep, enabled=factory, audit=factory_audit)
    return rep


def resolve_pack_dir(arg: str) -> Path:
    """A pack folder that works from any folder: a CWD-relative path wins, else the same
    path under the repo root, else a bare slug under packs/ (so `fleet-vol-1` finds
    packs/fleet-vol-1 when run from another checkout like center)."""
    p = Path(arg)
    if p.is_absolute():
        return p.resolve()
    cwd_p = (Path.cwd() / p).resolve()
    if cwd_p.is_dir():
        return cwd_p
    root_p = (ROOT / p).resolve()
    if root_p.is_dir():
        return root_p
    slug_p = (ROOT / "packs" / p.name).resolve()
    if slug_p.is_dir():
        return slug_p
    return cwd_p  # not found anywhere: report the CWD-relative path as before


def resolve_dist_dir(arg: str | None) -> Path | None:
    if arg is None:
        return None
    p = Path(arg)
    if p.is_absolute():
        return p.resolve()
    cwd_p = (Path.cwd() / p).resolve()
    if cwd_p.exists():
        return cwd_p
    root_p = (ROOT / p).resolve()
    if root_p.exists():
        return root_p
    return cwd_p


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", help="pack folder, e.g. packs/fleet-vol-1")
    ap.add_argument("--dist", default=None, help="folder that holds the built zips (default dist)")
    ap.add_argument("--offline", action="store_true", help="do not fetch the price evidence pages")
    ap.add_argument("--no-factory", action="store_true", help="skip the factory buyer-file gate")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    pack_dir = resolve_pack_dir(args.pack)
    if not pack_dir.is_dir():
        print(f"RESULT FAIL: {args.pack} is not a folder")
        return 1
    rep = check_pack(pack_dir, dist=resolve_dist_dir(args.dist), offline=args.offline,
                     factory=not args.no_factory)
    for level, what in rep.lines:
        print(f"{level} {what}")
    fails, needs, warns = rep.count("FAIL"), rep.count("NEEDS"), rep.count("WARN")
    tail = f"{pack_dir.name} ({rep.count('PASS')} checks pass, {warns} warnings, {needs} store assets still needed before it can go live)"
    print(f"RESULT {'FAIL' if fails else 'PASS'}: " + (f"{pack_dir.name} ({fails} findings)" if fails else tail))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
