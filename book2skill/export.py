"""Export stage: copy skill to agent target layouts. Gate: eval rate >= 0.6."""
from __future__ import annotations

import json
import os
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import click

from . import build as build_mod

TARGETS = ("claude", "codex", "opencode", "gemini")
GATE = 0.6
REPORT_FILENAME = "eval_report.json"

# K-53 R5: one build, four copy-layout exports. Same copy path for every
# target; only the layout root (out/<target>/<name>) differs. SKILL.md stays
# at the layout root so every target imports as-is; .lock.json marks the
# build and the ZIP beside the dir is the shippable artifact (K-41 shape).
# Donor ideas only: Skill_Seekers per-target copy layouts (MIT, read live
# 2026-10-03); no target-specific forks beyond this table.
LAYOUTS = {
    "claude": {"root_file": "SKILL.md", "lock": ".lock.json"},
    "codex": {"root_file": "SKILL.md", "lock": ".lock.json"},
    "opencode": {"root_file": "SKILL.md", "lock": ".lock.json"},
    "gemini": {"root_file": "SKILL.md", "lock": ".lock.json"},
}


def layout_for(target: str) -> dict:
    """Layout descriptor for one export target (K-53); unknown targets stay a usage error."""
    try:
        return LAYOUTS[target]
    except KeyError:
        raise click.UsageError(f"unknown target {target}; legal: claude|codex|opencode|gemini") from None


def load_eval_report(skilldir: Path) -> dict | None:
    """Resolve the skill's latest eval report, if one was saved beside it."""
    path = skilldir / REPORT_FILENAME
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


OUTPUT_DIR = "export"   # the usual output folder; git-ignored as skills/*/export/
# Windows MAX_PATH is 260. On 2026-10-03 the exporter copied a skill into itself and made paths
# of 200 to 5000 characters, which crashed the OpenCode file watcher 9 times.
MAX_DEST_PATH = 240


def _is_link(path: str) -> bool:
    """A symlink or a Windows junction: a copy must not follow it (a loop never ends)."""
    isjunction = getattr(os.path, "isjunction", None)
    return os.path.islink(path) or bool(isjunction and isjunction(path))


def _skip_names(skilldir: Path, out: Path, dest: Path | None = None) -> set[str]:
    """Top-level names of the skill dir that a copy must leave out (K-07 and the rest of its class).

    The usual output folder, always (an old export/ left in the skill must not ship). The top
    folder that holds --out or the destination when either sits inside the skill dir. With
    --out at the skill dir itself, the target folders an earlier export wrote there.
    """
    root = skilldir.resolve()
    skip = {OUTPUT_DIR}
    for place in (out, dest):
        if place is None:
            continue
        try:
            rel = place.resolve().relative_to(root)
        except ValueError:
            continue
        if rel.parts:
            skip.add(rel.parts[0])
        elif place is out:
            skip.update(TARGETS)
    return skip


def _own_output_ignore(skilldir: Path, out: Path, dest: Path | None = None):
    """Ignore function so copytree never copies our own output or follows a link (K-07).

    Without it, --out inside the skill dir (skills/<name>/export, or the skill dir itself) makes
    copytree recurse into its own destination: export/<target>/<name>/export/... nesting.
    """
    root = skilldir.resolve()
    skip = _skip_names(skilldir, out, dest)

    def _ignore(src: str, names: list[str]) -> list[str]:
        hide = [n for n in names if _is_link(os.path.join(src, n))]
        if Path(src).resolve() == root:
            hide += [n for n in names if n in skip and n not in hide]
        return hide

    return _ignore


def _refuse(why: str) -> None:
    raise SystemExit(f"export refused: {why}")


def _check_paths(skilldir: Path, out: Path, dest: Path) -> None:
    """Stop before any copy or delete when the paths would eat the source or run past the limit."""
    src, dst = skilldir.resolve(), dest.resolve()
    if dst == src:
        _refuse(f"the destination {dst} is the skill dir itself; copying would delete the source")
    if dst in src.parents:
        _refuse(f"the destination {dst} is above the skill dir {src}; clearing it would delete the source")
    skip = _skip_names(skilldir, out, dest)
    base = len(str(dst))
    worst, worst_rel = base, ""
    for here, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if not _is_link(os.path.join(here, d)) and not (Path(here) == src and d in skip)]
        for name in files + dirs:
            rel = os.path.relpath(os.path.join(here, name), src)
            if base + 1 + len(rel) > worst:
                worst, worst_rel = base + 1 + len(rel), rel
    if worst > MAX_DEST_PATH:
        _refuse(
            f"{worst} characters at {dst}{os.sep}{worst_rel[:60]}... (limit {MAX_DEST_PATH}); "
            "a path this long usually means the skill holds a copy of itself"
        )


# Reproducible-ZIP pattern (donor: pypa/hatch, MIT,
# https://github.com/pypa/hatch/blob/main/backend/src/hatchling/builders/utils.py:
# get_reproducible_timestamp default 1580601600, normalize_file_permissions,
# set_zip_info_mode; wheel.py WheelArchive fixes ZipInfo time_tuple).
# Ported fresh in our style: fixed ZipInfo time_tuple (SOURCE_DATE_EPOCH-aware)
# and normalized perms (644/755); stdlib zipfile only.
_REPRODUCIBLE_EPOCH_DEFAULT = 1580601600


def _reproducible_time_tuple() -> tuple:
    """Fixed ZipInfo date_time so the same bytes hash the same (SOURCE_DATE_EPOCH-aware)."""
    raw = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    try:
        stamp = int(raw) if raw else _REPRODUCIBLE_EPOCH_DEFAULT
    except ValueError:
        stamp = _REPRODUCIBLE_EPOCH_DEFAULT
    return datetime.fromtimestamp(stamp, timezone.utc).timetuple()[:6]


def _normalized_zip_mode(full: str) -> int:
    """Executable stays 755, everything else 644, whatever the checkout umask was."""
    try:
        mode = os.stat(full).st_mode
    except OSError:
        return 0o644
    return 0o755 if (mode & 0o111) else 0o644


def _write_zip(dest: Path, zip_path: Path) -> list[str]:
    """Bundle the exported copy as a store-ready ZIP (K-41, STEAL-ZIP).

    SKILL.md sits at the root (arcname ``SKILL.md``, not ``<name>/SKILL.md``) so the
    archive imports as a skill as-is. Dotfiles (``.lock.json`` et al) and links are
    skipped; everything else the copy shipped (references/, scripts/, assets/,
    chapters/, ...) rides along. The ZIP lives beside the exported dir
    (``out/<target>/<name>.zip``), never inside it, so a later export never copies
    the archive into itself. Donor idea: yusufkaraaslan/Skill_Seekers
    ``cli/adaptors/claude.py`` (MIT, read live 2026-10-03); stdlib zipfile only.
    Reproducible-ZIP donor: pypa/hatch (MIT, link above); entries share one fixed
    time_tuple and normalized perms so reruns are byte-identical.
    """
    stamp = _reproducible_time_tuple()
    names: list[str] = []
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as bundle:
        for here, dirs, files in os.walk(dest):
            dirs[:] = sorted(
                d for d in dirs
                if not d.startswith(".") and not _is_link(os.path.join(here, d))
            )
            for name in sorted(files):
                if name.startswith("."):
                    continue
                full = os.path.join(here, name)
                if _is_link(full):
                    continue
                arc = os.path.relpath(full, dest).replace(os.sep, "/")
                if arc.startswith(".") or "/." in arc:
                    continue
                info = zipfile.ZipInfo(arc, date_time=stamp)
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = (_normalized_zip_mode(full) << 16)
                with open(full, "rb") as handle:
                    bundle.writestr(info, handle.read())
                names.append(arc)
    return names


# Steal: same-version re-export gate (clawhub slug+semver-duplicate refuse).
# Donor: openclaw/clawhub (MIT,
# https://github.com/openclaw/clawhub/blob/main/convex/lib/skillPublish.ts:
# normalizeSkillSlug + semver.valid + "Version X already exists" refuse BEFORE
# artifact write; cf. issue #3677 orphan-ZIP leak). Ported fresh in our style:
# normalize the slug, compare SKILL.md version vs the existing dest
# .lock.json version, and refuse (exit 2, one line) before any rmtree/copytree/ZIP.
def _normalize_slug(slug: str) -> str:
    """Lowercase file-safe slug so `Demo_Skill` and `demo-skill` count as one."""
    return re.sub(r"[^a-z0-9]+", "-", slug.lower()).strip("-")


def _refuse_same_version(skilldir: Path, dest: Path) -> None:
    """Refuse a silent same-version re-export before any artifact is touched."""
    lock_path = dest / ".lock.json"
    if not lock_path.is_file():
        return
    try:
        existing = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    current_version = skill_version(skilldir).strip()
    existing_version = str(existing.get("version", "")).strip()
    if not current_version or not existing_version:
        return
    if _normalize_slug(str(existing.get("name", ""))) != _normalize_slug(skilldir.name):
        return
    if existing_version == current_version:
        msg = (
            f"export refused: Version {current_version} of '{skilldir.name}' already exists "
            f"in {dest}; bump SKILL.md version to ship again"
        )
        err = SystemExit(msg)
        err.code = 2
        raise err


def skill_version(skilldir: Path) -> str:
    """Version from SKILL.md frontmatter (K-18); default 0.1.0 when missing."""
    try:
        text = (skilldir / "SKILL.md").read_text(encoding="utf-8")
    except OSError:
        return "0.1.0"
    if not text.startswith("---"):
        return "0.1.0"
    head = text.split("---", 2)[1] if text.count("---") >= 2 else ""
    m = re.search(r"^version:\s*(\S+)", head, re.M)
    return m.group(1) if m else "0.1.0"


def export(skilldir: Path, target: str, out: Path, eval_report: dict | None = None) -> dict:
    layout = layout_for(target)
    report = eval_report if eval_report is not None else load_eval_report(skilldir)
    if report is None:
        raise SystemExit(
            f"eval gate refused export: no eval report found for '{skilldir.name}'; "
            "run eval first (--work/--qa) and fix the skill first"
        )
    rate = float(report.get("rate", 0.0))
    if rate < GATE:
        raise SystemExit(
            f"eval gate refused export: rate {rate:.3f} below {GATE:.1f}; fix the skill first"
        )
    build_mod.refuse_nc_price(skilldir)  # K-48 slice (1): an NC source never gets a price
    left = build_mod.scaffold_leftovers(skilldir)
    if left:
        raise SystemExit("export held: " + ", ".join(left) + " still hold the scaffold text; write them first (a pack with placeholder text is not shipped)")
    dest = out / target / skilldir.name
    _check_paths(skilldir, out, dest)
    _refuse_same_version(skilldir, dest)
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(skilldir, dest, ignore=_own_output_ignore(skilldir, out, dest))
    lock = {
        "name": skilldir.name,
        "version": skill_version(skilldir),
        "eval-rate": rate,
        "target": target,
        "date": datetime.now(timezone.utc).date().isoformat(),
    }
    (dest / ".lock.json").write_text(json.dumps(lock, indent=2), encoding="utf-8")
    zip_path = out / target / f"{skilldir.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    members = _write_zip(dest, zip_path)
    receipt = {"stage": "export", "target": target, "dest": str(dest),
               "zip": str(zip_path), "zip_files": len(members),
               "root_file": layout["root_file"]}
    print(json.dumps(receipt, indent=2))
    return receipt
