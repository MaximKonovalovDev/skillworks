"""Preview-then-install helper: full SKILL.md + source repo + install count.

Attribution: idea-level port (written fresh, no donor code copied) from
skillsgate/skillsgate@7acf56e apps/web/src/routes/_index.tsx (licence MIT,
https://github.com/skillsgate/skillsgate): Discover preview-then-install =
read the full SKILL.md plus check the install count plus open the source
repo before installing, moving blind installs toward informed installs.

This module is stdlib-only (pathlib/json/re only) and local-only: it reads
SKILL.md, references/sources.md and eval_report.json from disk and never
touches the network. It returns a plain JSON-serializable preview dict plus
a human-readable block the MCP server can serve later (e.g. beside
skill_preview/skill_install) without editing mcp_server/server.py.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SKILLS_DIR = ROOT / "skills"

SKILL_FILENAME = "SKILL.md"
SOURCES_FILENAME = Path("references") / "sources.md"
EVAL_REPORT_FILENAME = "eval_report.json"

_GITHUB_RE = re.compile(r"https://github\.com/[A-Za-z0-9_.\-]+/[A-Za-z0-9_.\-]+")

DONOR = "skillsgate/skillsgate@7acf56e"
DONOR_FILE = "apps/web/src/routes/_index.tsx"
DONOR_LICENCE = "MIT"
DONOR_URL = "https://github.com/skillsgate/skillsgate"


def is_safe_skill_name(name: object) -> bool:
    """True for a plain skill dirname; rejects traversal and separators."""
    if not isinstance(name, str):
        return False
    if not name or name.strip() != name:
        return False
    if "/" in name or "\\" in name or ".." in name:
        return False
    if "\x00" in name:
        return False
    return True


def _skills_dir(skills_dir: str | Path | None = None) -> Path:
    if skills_dir is None:
        return DEFAULT_SKILLS_DIR
    return Path(skills_dir)


def read_skill_md(skill: str, skills_dir: str | Path | None = None) -> str:
    """Full SKILL.md text for one skill; empty on bad names or missing files."""
    if not is_safe_skill_name(skill):
        return ""
    try:
        return (_skills_dir(skills_dir) / skill / SKILL_FILENAME).read_text(encoding="utf-8")
    except OSError:
        return ""


def read_source_repo(skill: str, skills_dir: str | Path | None = None) -> str:
    """First github.com owner/repo URL for one skill, else empty string.

    Search order (local files only): references/sources.md first, then
    the SKILL.md body. Returns the bare https://github.com/<owner>/<repo>
    URL (trailing path/punctuation stripped) so the caller can open the
    source repo before installing.
    """
    if not is_safe_skill_name(skill):
        return ""
    base = _skills_dir(skills_dir) / skill
    candidates: list[str] = []
    try:
        candidates.append((base / SOURCES_FILENAME).read_text(encoding="utf-8"))
    except OSError:
        pass
    skill_md = read_skill_md(skill, skills_dir)
    if skill_md:
        candidates.append(skill_md)
    for text in candidates:
        match = _GITHUB_RE.search(text)
        if match:
            return match.group(0).rstrip(").,;:'\"")
    return ""


def read_install_count(skill: str, skills_dir: str | Path | None = None) -> int:
    """Local install count: 1 when SKILL.md exists, else 0 (honest, local-only)."""
    if not is_safe_skill_name(skill):
        return 0
    try:
        return 1 if (_skills_dir(skills_dir) / skill / SKILL_FILENAME).exists() else 0
    except OSError:
        return 0


def read_downloads(skill: str, skills_dir: str | Path | None = None) -> int:
    """Eval passed-count proxy for registry-style download counts; 0 when unknown."""
    if not is_safe_skill_name(skill):
        return 0
    try:
        report = json.loads(
            (_skills_dir(skills_dir) / skill / EVAL_REPORT_FILENAME).read_text(encoding="utf-8")
        )
    except (OSError, ValueError):
        return 0
    try:
        passed = int(report.get("passed", 0))
    except (TypeError, ValueError, AttributeError):
        return 0
    return passed if passed >= 0 else 0


def format_preview_block(preview: dict) -> str:
    """Render a preview dict as a preview-then-install text block.

    The block carries all three informed-install fields: the full SKILL.md,
    the source repo line and the install-count line, so an installer reads
    them before installing instead of installing blind.
    """
    skill = str(preview.get("skill", ""))
    skill_md = str(preview.get("skill_md", ""))
    source_repo = str(preview.get("source_repo", ""))
    installs = preview.get("install_count", preview.get("installs", 0))
    downloads = preview.get("downloads", 0)
    try:
        installs_i = int(installs)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        installs_i = 0
    try:
        downloads_i = int(downloads)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        downloads_i = 0
    source_line = source_repo if source_repo else "(unknown source repo)"
    lines = [
        f"=== preview: {skill} ===",
        f"source repo: {source_line}",
        f"install count: {installs_i} (downloads/eval-passed proxy: {downloads_i})",
        f"--- SKILL.md (full, {len(skill_md)} chars) ---",
        skill_md if skill_md else "(no SKILL.md found)",
        "--- end preview: read the SKILL.md plus source repo plus counts before installing ---",
    ]
    return "\n".join(lines)


def build_preview(skill: str, skills_dir: str | Path | None = None) -> dict:
    """Build the preview-then-install dict for one skill (JSON-serializable).

    Returns {"ok": True, skill, file, skill_md (full, never truncated),
    chars, source_repo, installs, install_count, downloads, informed, block}
    on success, or {"ok": False, skill, error} for bad/unknown names. The
    server can serve this dict (or just preview["block"]) as-is later.
    """
    if not is_safe_skill_name(skill):
        return {"ok": False, "skill": str(skill), "error": f"bad skill name {str(skill)!r}"}
    skill_md = read_skill_md(skill, skills_dir)
    if not skill_md:
        base = _skills_dir(skills_dir)
        known = 0
        try:
            known = sum(1 for p in base.iterdir() if (p / SKILL_FILENAME).exists())
        except OSError:
            known = 0
        return {
            "ok": False,
            "skill": skill,
            "error": f"unknown skill {skill!r}; serving {known} skills from {base}",
        }
    source_repo = read_source_repo(skill, skills_dir)
    installs = read_install_count(skill, skills_dir)
    downloads = read_downloads(skill, skills_dir)
    preview = {
        "ok": True,
        "skill": skill,
        "file": SKILL_FILENAME,
        "skill_md": skill_md,
        "chars": len(skill_md),
        "source_repo": source_repo,
        "installs": installs,
        "install_count": installs,
        "downloads": downloads,
        "informed": True,
    }
    preview["block"] = format_preview_block(preview)
    return preview
