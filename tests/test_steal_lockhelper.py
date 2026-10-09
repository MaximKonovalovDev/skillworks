# Attribution: pattern steal from openclaw/clawhub@d044664
# packages/clawhub/src/skills.ts (MIT,
# https://github.com/openclaw/clawhub/blob/d044664a7636ec74b0092aa13fc0fcad1e660121/packages/clawhub/src/skills.ts):
# readLockfile/writeLockfile + lock.json
# (registry/slug/installedVersion/installedAt/fingerprint) + origin.json per
# skill. Fresh Python stdlib-only implementation; no donor code copied.
"""Steal lockhelper: install lockfile read/write moves unlocked installs to locked."""
import json
from pathlib import Path

import mcp_server.lock_helper as lh


def _skill(dest: Path, slug: str, version: str = "1.2.0", body: str = "Body.") -> Path:
    d = dest / slug
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {slug}\ndescription: Demo skill.\nversion: {version}\n---\n\n# {slug}\n{body}\n",
        encoding="utf-8",
    )
    return d


def test_read_empty_returns_default(tmp_path: Path) -> None:
    lock = lh.read_lockfile(tmp_path)
    assert lock == {"version": 1, "skills": {}}


def test_write_then_read_roundtrip(tmp_path: Path) -> None:
    origin = lh.make_origin("test-reg", "alpha", "1.2.0", fingerprint="ab" * 32, installed_at=1700000000000)
    lh.write_lockfile(tmp_path, {"version": 1, "skills": {"alpha": origin}})
    back = lh.read_lockfile(tmp_path)
    assert set(back["skills"]) == {"alpha"}
    entry = back["skills"]["alpha"]
    assert entry["registry"] == "test-reg"
    assert entry["slug"] == "alpha"
    assert entry["installedVersion"] == "1.2.0"
    assert entry["installedAt"] == 1700000000000
    assert entry["fingerprint"] == "ab" * 32
    raw = json.loads((tmp_path / ".clawhub" / "lock.json").read_text(encoding="utf-8"))
    assert raw["skills"]["alpha"]["installedVersion"] == "1.2.0"


def test_corrupt_lock_returns_default(tmp_path: Path) -> None:
    dot = tmp_path / ".clawhub"
    dot.mkdir(parents=True)
    (dot / "lock.json").write_text("{not json", encoding="utf-8")
    assert lh.read_lockfile(tmp_path) == {"version": 1, "skills": {}}
    (dot / "lock.json").write_text(json.dumps({"version": 99, "skills": {}}), encoding="utf-8")
    assert lh.read_lockfile(tmp_path) == {"version": 1, "skills": {}}


def test_origin_roundtrip_and_validation(tmp_path: Path) -> None:
    d = _skill(tmp_path / "skills", "alpha", "0.3.1")
    origin = lh.make_origin("r", "alpha", "0.3.1", fingerprint=lh.fingerprint_skill(d), installed_at=1700000000000)
    lh.write_skill_origin(d, origin)
    back = lh.read_skill_origin(d)
    assert back is not None and back["slug"] == "alpha" and back["installedVersion"] == "0.3.1"
    assert (d / ".clawhub" / "origin.json").is_file()
    bad = dict(origin)
    bad["version"] = 99
    (d / ".clawhub" / "origin.json").write_text(json.dumps(bad), encoding="utf-8")
    assert lh.read_skill_origin(d) is None
    bad2 = dict(origin, version=1)
    del bad2["installedVersion"]
    (d / ".clawhub" / "origin.json").write_text(json.dumps(bad2), encoding="utf-8")
    assert lh.read_skill_origin(d) is None


def test_fingerprint_stable_and_sensitive(tmp_path: Path) -> None:
    d = _skill(tmp_path / "skills", "alpha")
    first = lh.fingerprint_skill(d)
    assert first == lh.fingerprint_skill(d)
    assert len(first) == 64
    (d / "SKILL.md").write_text((d / "SKILL.md").read_text(encoding="utf-8") + "\nExtra.\n", encoding="utf-8")
    assert lh.fingerprint_skill(d) != first
    (d / ".clawhub" / "junk.txt").parent.mkdir(parents=True, exist_ok=True)
    (d / ".clawhub" / "junk.txt").write_text("noise", encoding="utf-8")
    assert lh.fingerprint_skill(d) == lh.hash_skill_files(d)["fingerprint"]


def test_list_manual_skills_finds_unlocked(tmp_path: Path) -> None:
    skills = tmp_path / "skills"
    _skill(skills, "alpha")
    _skill(skills, "beta")
    assert lh.list_manual_skills(skills, set()) == ["alpha", "beta"]
    assert lh.list_manual_skills(skills, {"alpha"}) == ["beta"]
    lock = {"version": 1, "skills": {"alpha": lh.make_origin("r", "alpha", "1.2.0", installed_at=1)}}
    assert lh.list_manual_skills(skills, lock) == ["beta"]


def test_adopt_moves_unlocked_to_locked(tmp_path: Path) -> None:
    work = tmp_path / "work"
    skills = work / "skills"
    _skill(skills, "alpha", "1.2.0")
    _skill(skills, "beta", "0.3.1")
    assert lh.read_lockfile(work) == {"version": 1, "skills": {}}
    adopted = lh.adopt_installed_without_lock(skills, workdir=work, registry="test-reg", now=1700000000000)
    assert adopted == ["alpha", "beta"]
    lock = lh.read_lockfile(work)
    assert set(lock["skills"]) == {"alpha", "beta"}
    for slug, want in (("alpha", "1.2.0"), ("beta", "0.3.1")):
        entry = lock["skills"][slug]
        assert entry["registry"] == "test-reg"
        assert entry["slug"] == slug
        assert entry["installedVersion"] == want
        assert entry["installedAt"] == 1700000000000
        assert len(entry["fingerprint"]) == 64
        origin = lh.read_skill_origin(skills / slug)
        assert origin == entry
    assert lh.list_manual_skills(skills, lh.locked_slugs(lock)) == []
    assert lh.adopt_installed_without_lock(skills, workdir=work, registry="test-reg") == []
    assert lh.ensure_locked_skills(skills, workdir=work, registry="test-reg") == []


def test_adopt_preserves_existing_origin(tmp_path: Path) -> None:
    work = tmp_path / "work"
    skills = work / "skills"
    d = _skill(skills, "alpha", "1.2.0")
    keep = lh.make_origin("keep-reg", "alpha", "1.2.0", fingerprint="cd" * 32, installed_at=1700000000001)
    lh.write_skill_origin(d, keep)
    adopted = lh.adopt_installed_without_lock(skills, workdir=work, registry="other-reg", now=1700000000000)
    assert adopted == ["alpha"]
    lock = lh.read_lockfile(work)
    assert lock["skills"]["alpha"]["registry"] == "keep-reg"
    assert lock["skills"]["alpha"]["installedAt"] == 1700000000001
    assert lock["skills"]["alpha"]["fingerprint"] == "cd" * 32
