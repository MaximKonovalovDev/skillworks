"""Build the buyer files of a pack: python tools/pack_build.py packs/<slug> [--dist dist]

A pack folder holds `pack.json` (title, version, price, the skills, the free Vol 0 skill), `README-buyer.md`, the
listing and the sample text. This tool writes into `dist/` (git-ignored, never inside `skills/`):

  dist/<slug>.zip          the paid pack: README.md, LICENSES.md, manifest.json (path, size, sha256 of every file),
                           skills/<name>/ (the files the installer copies), zips/<name>.zip (one skill per zip,
                           SKILL.md at the root), proof/<name>-live-proof.json
  dist/<slug>-vol0.zip     the free Vol 0 skill: SKILL.md at the root plus NOTICE.md with its licence

The zips are reproducible: sorted names, a fixed time stamp, no extra attributes. The same sources give the same
bytes, so `pack_check.py` can rebuild in memory and prove the file in `dist/` is current.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import install_fleet_skills as inst  # noqa: E402  (the one definition of which skill files a copy holds)

STAMP = (2026, 1, 1, 0, 0, 0)
MAX_BUNDLE_BYTES = 5 * 1024 * 1024


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


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pack", help="pack folder, e.g. packs/fleet-vol-1")
    ap.add_argument("--dist", default=str(ROOT / "dist"), help="output folder (default dist; never inside skills/)")
    args = ap.parse_args(argv)
    dist = Path(args.dist).resolve()
    if (ROOT / "skills").resolve() in [dist, *dist.parents]:
        print(f"ERROR refused: --dist {dist} is inside skills/ (a nested output crashed the OpenCode server 9 times)")
        return 2
    for path in build(Path(args.pack), dist):
        print(f"built {path} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
