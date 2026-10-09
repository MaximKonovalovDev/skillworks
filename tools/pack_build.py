"""Build the buyer files of a pack: python tools/pack_build.py packs/<slug> [--dist dist]

A pack folder holds `pack.json` (title, version, price, the skills, the free Vol 0 skill), `README-buyer.md`, the
listing and the sample text. This tool writes into `dist/` (git-ignored, never inside `skills/`):

  dist/<slug>.zip          the paid pack: README.md, LICENSES.md, manifest.json (path, size, sha256 of every file),
                           skills/<name>/ (the files the installer copies), zips/<name>.zip (one skill per zip,
                           SKILL.md at the root), proof/<name>-live-proof.json
  dist/<slug>-vol0.zip     the free Vol 0 skill: SKILL.md at the root plus NOTICE.md with its licence

The zips are reproducible: sorted names, a fixed time stamp, no extra attributes. The same sources give the same
bytes, so `pack_check.py` can rebuild in memory and prove the file in `dist/` is current.

    python tools/pack_build.py packs/<slug> --starter [--skills skills]

writes the four files a new pack starts from, prefilled from its `pack.json` (name, version, counts, price, licences, the
proof lines of each skill's `live-proof.json`): `listing.md` with every heading and field `pack_check.py` requires,
`README-buyer.md` and `vol0-sample.md` shaped like the ones of `packs/fleet-vol-1/`, and `price.txt`. What only a person can
write is a slot line, `{{slot: what to write}}`; `pack_check.py` reports each open slot as a finding until it is written.
It builds nothing, and refuses to overwrite: when any of the four files exists it writes none of them.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import io
import json
import re
import struct
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import install_fleet_skills as inst  # noqa: E402  (the one definition of which skill files a copy holds)

STAMP = (2026, 1, 1, 0, 0, 0)
MAX_BUNDLE_BYTES = 5 * 1024 * 1024
MIN_COVER_WIDTH = 1280
MIN_COVER_HEIGHT = 720

# Cover dimensions ported from image-size/image-size (MIT, https://github.com/image-size/image-size):
# lib/detector.ts firstBytes dispatch + lib/types/png.ts IHDR reader.
# Rewritten here stdlib-only with struct reads of the PNG IHDR and GIF header.
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
GIF_MAGICS = (b"GIF87a", b"GIF89a")


def cover_dimensions(path):
    # (width, height) of a PNG or GIF cover from its header stdlib-only.
    # Raises FileNotFoundError when missing and ValueError when not PNG or GIF.
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"cover not found: {p}")
    data = p.read_bytes()
    if data[:8] == PNG_MAGIC:
        if len(data) < 24:
            raise ValueError(f"truncated PNG cover: {p}")
        (length,) = struct.unpack(">I", data[8:12])
        if data[12:16] != b"IHDR":
            raise ValueError(f"PNG cover first chunk is not IHDR: {p}")
        if length < 13 or len(data) < 24:
            raise ValueError(f"truncated PNG IHDR: {p}")
        (width, height) = struct.unpack(">II", data[16:24])
        return (width, height)
    if data[:6] in GIF_MAGICS:
        if len(data) < 10:
            raise ValueError(f"truncated GIF cover: {p}")
        (width, height) = struct.unpack("<HH", data[6:10])
        return (width, height)
    raise ValueError(f"not a PNG or GIF cover: {p}")


def cover_warning(path):
    # Warning when a store cover is smaller than the minimum, else None.
    (width, height) = cover_dimensions(path)
    if width < MIN_COVER_WIDTH or height < MIN_COVER_HEIGHT:
        return f"{Path(path).name} is {width}x{height}, want {MIN_COVER_WIDTH}x{MIN_COVER_HEIGHT}+"
    return None

# The shape of a listing.md, once. The starter below writes it and tools/pack_check.py requires it: both read these two
# constants, so the starter and the gate cannot disagree. The headings are in the order of packs/fleet-vol-1/listing.md.
# Each section is (heading as written, the lowercase key pack_check matches by prefix, or None when the heading is part
# of the shape but not a gate). LISTING_FIELDS are the "Key: value" lines every listing carries.
LISTING_FIELDS = ("Status", "Price", "AI disclosure", "Category", "Tags", "Author", "Repository", "Stars", "Weekly installs", "Sales")
LISTING_SECTIONS = (
    ("What it is", None),
    ("What is inside", "what is inside"),
    ("Requirements", "requirements"),
    ("Install", "install"),
    ("Free sample (Vol 0)", "free sample"),
    ("Price", None),
    ("Price evidence", "price evidence"),
    ("Licences", "licences"),
    ("Proof", "proof"),
    ("Store assets", "store assets"),
    ("Files", None),
    ("Changelog", None),
    ("Trust", None),
)
REQUIRED_SECTIONS = tuple(key for _, key in LISTING_SECTIONS if key)
STARTER_FILES = ("listing.md", "README-buyer.md", "vol0-sample.md", "price.txt")
SLOT_RE = re.compile(r"\{\{slot:\s*(.*?)\}\}")


# Changelog bump ported from maziyarpanahi/openmed@08c368f (Apache-2.0,
# https://github.com/maziyarpanahi/openmed/blob/08c368f558691776a5867442f5bf893e369f801e/scripts/release/changelog.py):
# conventional-commit subject parse + strongest major/minor/patch + Keep-a-Changelog line render +
# minimum-bump guard. Rewritten here stdlib-only with a small subject-line match.
CONVENTIONAL_RE = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\(.+\))?(!)?:\s*\S")
_BUMP_RANK = {"patch": 0, "minor": 1, "major": 2}


def commit_bump(msg: str) -> str:
    """The semver bump one conventional-commit subject asks for (major/minor/patch)."""
    text = msg or ""
    first = text.splitlines()[0] if text.strip() else ""
    if "BREAKING CHANGE" in text:
        return "major"
    m = CONVENTIONAL_RE.match(first.strip())
    if m and m.group(3):
        return "major"
    if m and m.group(1) == "feat":
        return "minor"
    return "patch"


def strongest_bump(msgs) -> str:
    """The strongest bump of many commit subjects (major wins, then minor, else patch)."""
    best = "patch"
    for msg in msgs or ():
        bump = commit_bump(msg)
        if _BUMP_RANK[bump] > _BUMP_RANK[best]:
            best = bump
    return best


def bump_version(version: str, bump: str) -> str:
    """The next semver after a bump (1.2.3 + major -> 2.0.0, minor -> 1.3.0, patch -> 1.2.4)."""
    major, minor, patch = (int(x) for x in str(version).strip().split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def minimum_version(old: str, bump: str) -> str:
    """The smallest new version a bump allows (the minimum-bump guard floor)."""
    return bump_version(old, bump)


def _semver_tuple(version: str) -> tuple[int, int, int]:
    parts = str(version).strip().split(".")
    return (int(parts[0]), int(parts[1]), int(parts[2]))


def meets_minimum_bump(old: str, new: str, bump: str) -> bool:
    """True when new is at least the minimum bump over old (the guard the starter line promises)."""
    return _semver_tuple(new) >= _semver_tuple(minimum_version(old, bump))


def changelog_line(today: str, version: str, bump: str) -> str:
    """One Keep-a-Changelog style line: date, version and the computed minimum bump (no slot)."""
    return f"- {today}: version {version} assembled. minimum {bump} bump (Keep a Changelog). Proof lines above say what was run."


# Attested-tier listing lines ported from roli-lpci/sigistry-marketplace@a7a30de (MIT,
# .claude-plugin/attestations.json + scripts/verify-plugins.mjs): code-verified badge + pinned sha +
# scope disclaimer + collision guard, never a catalog slot. Rewritten here as computed starter lines.
TRUST_BADGE = "code-verified"


def check_trust_collision(names) -> None:
    """Refuse a skill named like the Trust section (the collision guard): it would read as the badge."""
    lowered = [str(n).lower() for n in (names or [])]
    if "trust" in lowered:
        raise ValueError("skill name 'trust' collides with the ## Trust badge section")


def trust_lines(slug: str, sha: str, names=()) -> list[str]:
    """Computed Trust lines: badge + pinned sha + scope disclaimer + collision guard (never a catalog slot line)."""
    check_trust_collision([slug, *((names or ()))])
    pin = (sha or "unpinned").strip() or "unpinned"
    return [
        f"- Verified: `{TRUST_BADGE}` -- the Proof lines above ran against real programs; records are in `proof/`.",
        f"- Pinned source: `{pin}` (the commit the proofs ran against).",
        f"- Scope: this Trust covers `{slug}` only, not the whole catalog.",
        "- Collision guard: no skill in this pack is named `trust`, so the badge line cannot be mistaken for a skill.",
    ]


def load_pack(pack_dir: Path) -> dict:
    return json.loads((pack_dir / "pack.json").read_text(encoding="utf-8"))


def skill_files(name: str, skills: Path) -> dict[str, bytes]:
    """The files a copy of the skill holds, as relative posix path -> bytes (the installer's payload rule)."""
    base = skills / name
    out = {}
    for p in sorted(base.rglob("*")):
        rel = p.relative_to(base)
        if p.is_file() and p.name not in inst.SKIP_FILES and not (inst.SKIP_DIRS & set(rel.parts)):
            out[rel.as_posix()] = p.read_bytes()
    return out


def zip_bytes(files: dict[str, bytes]) -> bytes:
    """A reproducible zip: sorted names, fixed time stamp, deflate."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, date_time=STAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, files[name])
    return buf.getvalue()


def licences_text(pack: dict) -> str:
    lines = [f"# Licences and credits: {pack['title']}", "",
             "Every skill in this pack keeps the licence of its sources. Read the credit lines before you reuse or change one.", ""]
    for s in pack["skills"]:
        lines += [f"## {s['name']}", "", f"- Licence: {s['licence']}", f"- Credit: {s['credit']}", ""]
    lines += ["## Free Vol 0 (not part of this paid pack)", "",
              f"- {pack['vol0']['name']}: {pack['vol0']['licence']}. {pack['vol0']['credit']}", ""]
    return "\n".join(lines)


def pack_files(pack_dir: Path, pack: dict, skills: Path, text_files: dict[str, bytes] | None = None) -> dict[str, bytes]:
    """Every file of the paid zip except manifest.json (which lists them)."""
    files: dict[str, bytes] = {
        "README.md": (pack_dir / "README-buyer.md").read_bytes(),
        "LICENSES.md": licences_text(pack).encode("utf-8"),
    }
    for s in pack["skills"]:
        name = s["name"]
        body = skill_files(name, skills)
        for rel, data in body.items():
            files[f"skills/{name}/{rel}"] = data
        files[f"zips/{name}.zip"] = zip_bytes(body)
        proof = skills / name / "references" / "live-proof.json"
        if proof.is_file():
            files[f"proof/{name}-live-proof.json"] = proof.read_bytes()
    return files


def manifest_for(pack: dict, files: dict[str, bytes]) -> bytes:
    rows = [{"path": p, "size": len(files[p]), "sha256": hashlib.sha256(files[p]).hexdigest()} for p in sorted(files)]
    doc = {"pack": pack["slug"], "version": pack["version"], "skills": [s["name"] for s in pack["skills"]], "files": rows}
    return (json.dumps(doc, indent=2) + "\n").encode("utf-8")


def build_pack_zip(pack_dir: Path, pack: dict, skills: Path) -> bytes:
    files = pack_files(pack_dir, pack, skills)
    files["manifest.json"] = manifest_for(pack, files)
    return zip_bytes(files)


def build_vol0_zip(pack: dict, skills: Path) -> bytes:
    name = pack["vol0"]["name"]
    files = skill_files(name, skills)
    notice = (f"# {name}: licence\n\n{pack['vol0']['licence']}\n\n{pack['vol0']['credit']}\n\n"
              "This free skill is shared under the licence above: use it, share it, keep the credit, and share changes under the same licence. "
              "It is never sold.\n")
    files["NOTICE.md"] = notice.encode("utf-8")
    return zip_bytes(files)


def build(pack_dir: Path, dist: Path, skills: Path | None = None) -> list[Path]:
    skills = skills or ROOT / "skills"
    pack = load_pack(pack_dir)
    dist.mkdir(parents=True, exist_ok=True)
    out = []
    for fname, data in ((f"{pack['slug']}.zip", build_pack_zip(pack_dir, pack, skills)), (f"{pack['slug']}-vol0.zip", build_vol0_zip(pack, skills))):
        if len(data) > MAX_BUNDLE_BYTES:
            raise SystemExit(f"{fname} is {len(data)} bytes, over the {MAX_BUNDLE_BYTES} cap")
        (dist / fname).write_bytes(data)
        out.append(dist / fname)
    return out


def slot(what: str) -> str:
    """A slot line: text only a person can write. pack_check.py reports each open one as a finding."""
    assert "}}" not in what
    return "{{slot: " + what + "}}"


def open_slots(text: str) -> list[tuple[int, str]]:
    """(line number, what to write) for each open slot in a text."""
    return [(text.count("\n", 0, m.start()) + 1, m.group(1).strip()) for m in SLOT_RE.finditer(text)]


def proof_line(name: str, skills: Path) -> str:
    """The Proof line of one skill, from its live-proof.json (date and passed count), or a slot when it has none."""
    try:
        data = json.loads((skills / name / "references" / "live-proof.json").read_text(encoding="utf-8"))
        passed = re.match(r"\d+ passed", data["result"]).group(0)
        return f"- `{name}`: {data['date'][:10]}, {passed} ({slot('what the tests ran against')})."
    except (OSError, ValueError, KeyError, AttributeError):
        return f"- `{name}`: {slot('date and N passed from skills/' + name + '/references/live-proof.json; run python tests/live_proof.py ' + name)}"


def listing_starter(pack: dict, skills: Path, today: str, commits: tuple = (), sha: str = "unpinned") -> str:
    """listing.md with every field and heading of LISTING_FIELDS and LISTING_SECTIONS, prefilled from pack.json."""
    slug, title, version, vol0 = pack["slug"], pack["title"], pack["version"], pack["vol0"]
    price = f"${pack['price_usd']:g}"
    names = [s["name"] for s in pack["skills"]]
    fields = {
        "Status": slot("not live yet, or live on <store> since <date>; once the page is live add a line that starts with Live listing: and its https URL"),
        "Price": price,
        "AI disclosure": "generated: " + slot("what the AI wrote, and what was run and checked afterwards"),
        "Category": slot("the store category, for example Tool"),
        "Tags": slot("5 or 6 tags, comma separated"),
        "Author": slot("the author or the store display name"),
        "Repository": slot("https URL of the public repository"),
        "Stars": "0 (not listed, no stars)",
        "Weekly installs": "0 (not listed, no installs)",
        "Sales": "0 (stays 0 until a real sale; views and drafts are not sales)",
    }
    bodies = {
        "What it is": [slot("two to four sentences: what Agent Skills are, what mistake these fix, and why the claims can be trusted (what was run)")],
        "What is inside": [f"Pack file `{slug}.zip`, version {version}. Each skill is a folder in `skills/` and also its own zip in `zips/`.", "",
                           "| Skill | What it fixes | What was run |", "|---|---|---|",
                           *[f"| `{n}` | {slot('the mistake it fixes')} | {slot('what was run, with the counts')} |" for n in names]],
        "Requirements": [f"- `{n}`: {slot('what must be installed, and on which system it was measured')}" for n in names],
        "Install": [f"1. Unzip `{slug}.zip`.",
                    "2. Copy the folders in `skills/` to `$HOME\\.claude\\skills` for Claude Code, or to `$HOME\\.config\\opencode\\skills` for",
                    "   OpenCode (or the `.claude\\skills` or `.opencode\\skills` folder of one project).",
                    "3. A tool that takes one skill per zip uses `zips/<skill name>.zip`; SKILL.md is at the root of each.",
                    "4. Check: ask the agent which skills it has, or run `opencode debug skill --pure` in an OpenCode project.", "",
                    "The exact PowerShell commands are in `README.md` inside the zip.", "",
                    slot("a 15-minute try-it a stranger can run, or say that no stranger run has been done yet")],
        "Free sample (Vol 0)": [f"`{slug}-vol0.zip` is `{vol0['name']}`. It is free, never sold, and licensed {vol0['licence']}. It is not in the paid zip. "
                                f"{slot('one sentence: what it shows of the style of the pack')} See `vol0-sample.md`."],
        "Price": [f"{price} once. The pack is {len(names)} skills, with every file listed in `manifest.json`. "
                  f"{slot('how the take-home was worked out from the store fee page, and the date')}"],
        "Price evidence": [f"Sellers' own pages for {slot('the kind of pack')}, read {slot('date')}. They show what buyers are asked to pay today:", "",
                           *[f"- {slot('https URL of a seller page: what it asks and what it sells')}"] * 3, "",
                           slot("two sentences: where this price sits against those pages, and why")],
        "Licences": [*[f"- `{s['name']}`: {s['licence']}. {slot('where the text and the code come from, in one sentence')}" for s in pack["skills"]],
                     f"- No NonCommercial source is in the paid zip. `{vol0['name']}` ({vol0['licence']}) is the free Vol 0 only.", "",
                     "The full credit lines are in `LICENSES.md` inside the zip."],
        "Proof": ["Each skill has a live proof: its tests ran against real programs and the skill still matches the fingerprint stored then.", "",
                  *[proof_line(n, skills) for n in names], "", "The records are in `proof/` inside the zip."],
        "Store assets": [slot("one line: each asset below is a request until its file exists; none is faked"), "",
                         f"- cover: needed: {slot('size, content and style of the cover')}",
                         f"- demo: needed: {slot('a real screen capture: length, size limit and what it shows')}",
                         f"- screenshots: needed: {slot('how many real captures, their size and what each shows')}"],
        "Files": [f"- `{slug}.zip`: the paid pack (README.md, LICENSES.md, manifest.json, skills/, zips/, proof/).",
                  f"- `{slug}-vol0.zip`: the free Vol 0 skill (SKILL.md at the root, NOTICE.md)."],
        "Changelog": [changelog_line(today, version, strongest_bump(commits))],
        "Trust": trust_lines(slug, sha, names),
    }
    out = [f"# {title}", "", f"Tagline: {slot('one line of 60 to 110 characters: what the pack does for the buyer')}", ""]
    out += [f"{key}: {fields[key]}" for key in LISTING_FIELDS]
    for heading, _ in LISTING_SECTIONS:
        out += ["", f"## {heading}", "", *bodies[heading]]
    return "\n".join(out) + "\n"


def readme_starter(pack: dict) -> str:
    """README-buyer.md, the text that ships as README.md in the paid zip, shaped like packs/fleet-vol-1/README-buyer.md."""
    slug, title, version = pack["slug"], pack["title"], pack["version"]
    names = [s["name"] for s in pack["skills"]]
    out = [f"# {title}", "",
           f"Version {version}. {len(names)} Agent Skills (folders with a `SKILL.md`) for Claude Code, OpenCode and any other tool that reads `SKILL.md` folders. "
           f"{slot('one sentence: what mistake they fix, and that every claim was run on a real program before it was written down')}", "",
           "| Skill | What it fixes |", "|---|---|",
           *[f"| `{n}` | {slot('the mistake it fixes and what the skill gives')} |" for n in names], "",
           "## Requirements", "",
           *[f"- `{n}`: {slot('what must be installed, and on which system it was measured')}" for n in names], "",
           "## Install", "", "Unpack the zip, then copy the skill folders to where your agent looks for skills. In PowerShell 7:", "",
           "```powershell",
           f"Expand-Archive -LiteralPath {slug}.zip -DestinationPath {slug}",
           '$dest = "$HOME\\.claude\\skills"',
           "New-Item -ItemType Directory -Force -Path $dest | Out-Null",
           f'Copy-Item -Recurse -Force -Path "{slug}\\skills\\*" -Destination $dest',
           "```", "",
           "- Claude Code: `$HOME\\.claude\\skills` (every project) or `.claude\\skills` inside one project.",
           "- OpenCode: `$HOME\\.config\\opencode\\skills` (every project) or `.opencode\\skills` inside one project.",
           "- A tool that takes one skill per zip: use `zips\\<skill name>.zip` (SKILL.md is at the root of each).",
           "- Keep one copy of a skill name per tool. Two folders with the same name make some tools list it twice.", "",
           "Check that it loaded: ask the agent which skills it has, or in OpenCode run `opencode debug skill --pure` in the project.", "",
           "## Licences", "",
           "Each skill keeps the licence of its sources. `LICENSES.md` has the credit line for each. The text and scripts you bought",
           "may be used and changed under those licences. Do not remove the credits.", "",
           "## Proof", "",
           "`proof/<skill>-live-proof.json` is the record of the last run of that skill's live tests: date, result line, and the",
           "versions of the programs it ran with. `manifest.json` lists every file with its size and sha256.", "",
           "## Limits", "",
           f"- {slot('what was measured where, and what was not tested')}",
           "- No support is promised. The skills are text and scripts you can read and change."]
    return "\n".join(out) + "\n"


def vol0_starter(pack: dict) -> str:
    """vol0-sample.md, the free sample page, shaped like packs/fleet-vol-1/vol0-sample.md."""
    vol0, slug = pack["vol0"], pack["slug"]
    short = pack["title"].split(":")[0].strip()
    out = [f"# Vol 0: {vol0['name']} (free sample of {short})", "",
           f"Licence: {vol0['licence']}. {vol0['credit']} It is shared free under that licence, never sold, and it is not in the paid zip.", "",
           f"Download: `{slug}-vol0.zip`. SKILL.md is at the root of the zip, with a `NOTICE.md` that repeats the licence.", "",
           "## What it fixes", "", slot("two or three sentences on the mistake, then a short list of the exact commands or error texts the skill covers"), "",
           "## How it was tested", "", slot("what was run against what, with the exact error texts recorded, and where the live proof is")]
    return "\n".join(out) + "\n"


def starter_files(pack: dict, skills: Path, today: str) -> dict[str, str]:
    """The four starter files as name -> text, in STARTER_FILES order. Raises KeyError when pack.json lacks a key."""
    return {"listing.md": listing_starter(pack, skills, today), "README-buyer.md": readme_starter(pack),
            "vol0-sample.md": vol0_starter(pack), "price.txt": f"${pack['price_usd']:g}\n"}


def write_starters(pack_dir: Path, skills: Path | None = None, today: str | None = None) -> list[Path]:
    """Write the starter files into the pack folder. Raises ValueError, with nothing written, when pack.json cannot be read or
    lacks a key, or when any of the four files already exists (this never overwrites)."""
    try:
        pack = load_pack(pack_dir)
    except (OSError, ValueError) as err:
        raise ValueError(f"cannot read {pack_dir / 'pack.json'} ({err}); write pack.json first") from None
    taken = [n for n in STARTER_FILES if (pack_dir / n).exists()]
    if taken:
        raise ValueError(f"{pack_dir.name} already has {', '.join(taken)}; nothing written")
    try:
        files = starter_files(pack, skills or ROOT / "skills", today or datetime.date.today().isoformat())
    except (KeyError, TypeError, AttributeError) as err:
        raise ValueError(f"pack.json lacks {err}: it needs slug, title, version, price_usd, skills[name, licence, credit] and vol0[name, licence, credit]") from None
    for name, text in files.items():
        (pack_dir / name).write_text(text, encoding="utf-8", newline="\n")
    return [pack_dir / n for n in files]


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", help="pack folder, e.g. packs/fleet-vol-1")
    ap.add_argument("--dist", default=str(ROOT / "dist"), help="output folder (default dist; never inside skills/)")
    ap.add_argument("--starter", action="store_true", help="write the starter listing.md, README-buyer.md, vol0-sample.md and price.txt; refuses to overwrite; builds nothing")
    ap.add_argument("--skills", default=str(ROOT / "skills"), help="skills folder to read live-proof.json from (with --starter)")
    args = ap.parse_args(argv)
    if args.starter:
        try:
            written = write_starters(Path(args.pack).resolve(), Path(args.skills).resolve())
        except ValueError as err:
            print(f"ERROR refused: {err}")
            return 2
        slots = 0
        for path in written:
            slots += len(open_slots(path.read_text(encoding="utf-8")))
            print(f"wrote {path}")
        print(f"{slots} open slots: write each one; python tools/pack_check.py {args.pack} lists them until none is left")
        return 0
    dist = Path(args.dist).resolve()
    if (ROOT / "skills").resolve() in [dist, *dist.parents]:
        print(f"ERROR refused: --dist {dist} is inside skills/ (a nested output crashed the OpenCode server 9 times)")
        return 2
    for path in build(Path(args.pack), dist):
        print(f"built {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
