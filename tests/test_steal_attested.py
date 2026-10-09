"""Attested trust tier (trust tiers 1->2): verified vs attested-unverified from local file."""
import hashlib
import inspect
import json
from pathlib import Path

import mcp_server.server as srv


def _reset_attestations(monkeypatch, path):
    monkeypatch.setattr(srv, "ATTESTATIONS_FILE", Path(path))
    srv._ATTESTATIONS_PINNED = {}


def test_trust_field_present_and_defaults():
    meta = srv._skill_meta("progit-branching")
    assert "attested" in meta and "trust" in meta
    assert isinstance(meta["attested"], bool)
    assert meta["trust"] in (srv.TRUST_VERIFIED, srv.TRUST_UNVERIFIED)
    assert srv.TRUST_VERIFIED == "verified"
    assert srv.TRUST_UNVERIFIED == "attested-unverified"
    # default with no local attestations file is unverified
    if not srv.ATTESTATIONS_FILE.exists():
        assert meta["attested"] is False
        assert meta["trust"] == srv.TRUST_UNVERIFIED
    hits = srv._search("branching", limit=5)
    assert hits, "expected branching hits"
    for h in hits:
        assert "attested" in h and "trust" in h
        assert h["trust"] in (srv.TRUST_VERIFIED, srv.TRUST_UNVERIFIED)
        assert h["attested"] == (h["trust"] == srv.TRUST_VERIFIED)
    # sort unchanged: gate-first order still holds
    keys = [(h["above_gate"], h["installed"], h["downloads"], h["score"]) for h in hits]
    assert keys == sorted(keys, reverse=True)


def test_verify_at_pinned_sha(tmp_path, monkeypatch):
    skill = "progit-branching"
    live = srv._skill_sha256(skill)
    assert len(live) == 64
    pin_file = tmp_path / "attestations.json"
    pin_file.write_text(json.dumps({skill: live}), encoding="utf-8")
    _reset_attestations(monkeypatch, pin_file)
    assert srv._attestations() == {skill: live}
    assert srv._is_attested(skill) is True
    assert srv._trust_for(skill) == srv.TRUST_VERIFIED
    meta = srv._skill_meta(skill)
    assert meta["attested"] is True and meta["trust"] == srv.TRUST_VERIFIED
    # wrong pinned sha fails closed
    pin_file.write_text(json.dumps({skill: "0" * 64}), encoding="utf-8")
    srv._ATTESTATIONS_PINNED = {}
    assert srv._is_attested(skill) is False
    assert srv._trust_for(skill) == srv.TRUST_UNVERIFIED
    # tampered bytes fail: pin old sha, change file via tmp skills dir
    tmp_skills = tmp_path / "skills"
    victim = tmp_skills / skill
    victim.mkdir(parents=True)
    (victim / "SKILL.md").write_text("original bytes", encoding="utf-8")
    orig_sha = hashlib.sha256(b"original bytes").hexdigest()
    pin_file.write_text(json.dumps({skill: orig_sha}), encoding="utf-8")
    srv._ATTESTATIONS_PINNED = {}
    monkeypatch.setattr(srv, "ATTESTATIONS_FILE", pin_file)
    real_dir = srv._skills_dir
    monkeypatch.setattr(srv, "_skills_dir", lambda: tmp_skills)
    try:
        assert srv._is_attested(skill) is True
        (victim / "SKILL.md").write_text("tampered bytes", encoding="utf-8")
        assert srv._is_attested(skill) is False
        assert srv._trust_for(skill) == srv.TRUST_UNVERIFIED
    finally:
        monkeypatch.setattr(srv, "_skills_dir", real_dir)


def test_name_collision_guard(tmp_path, monkeypatch):
    skill = "progit-branching"
    live = srv._skill_sha256(skill)
    pin_file = tmp_path / "attestations.json"
    pin_file.write_text(json.dumps({skill: live}), encoding="utf-8")
    _reset_attestations(monkeypatch, pin_file)
    assert srv._is_attested(skill) is True
    # case differs: exact case-sensitive match only
    assert srv._is_attested("Progit-Branching") is False
    assert srv._is_attested("PROGIT-BRANCHING") is False
    # traversal and separators never match
    for bad in ("progit-branching/extra", "progit-branching/../other", "../progit-branching", "", "a/b"):
        assert srv._is_attested(bad) is False, bad
        assert srv._skill_sha256(bad) == "" or isinstance(srv._skill_sha256(bad), str)
    assert srv._skill_sha256("progit-branching/../other") == ""
    assert srv._trust_for("Progit-Branching") == srv.TRUST_UNVERIFIED


def test_local_only_never_network(tmp_path, monkeypatch):
    assert isinstance(srv.ATTESTATIONS_FILE, Path)
    assert str(srv.ATTESTATIONS_FILE).startswith("/") or "://" not in str(srv.ATTESTATIONS_FILE)
    src = inspect.getsource(srv._attestations) + inspect.getsource(srv._skill_sha256) + inspect.getsource(srv._is_attested) + inspect.getsource(srv._trust_for)
    for token in ("urlopen", "requests", "httpx", "http.client", "socket", "urllib"):
        assert token not in src, token
    assert "ATTESTATIONS_FILE" in inspect.getsource(srv._attestations)
    # works offline from a local tmp file
    pin_file = tmp_path / "attestations.json"
    pin_file.write_text(json.dumps({"x": "y"}), encoding="utf-8")
    _reset_attestations(monkeypatch, pin_file)
    assert srv._attestations() == {"x": "y"}


def test_attribution_present():
    text = Path("mcp_server/server.py").read_text(encoding="utf-8")
    if "mcp_server/server.py" not in text[:50]:
        text = (Path(__file__).resolve().parent.parent / "mcp_server" / "server.py").read_text(encoding="utf-8")
    assert "roli-lpci/sigistry-marketplace" in text
    assert "MIT" in text
    assert "verify-plugins.mjs" in text
    assert "https://github.com/roli-lpci/sigistry-marketplace/blob/a7a30de6bb3e6ba7b60e5b885513721f0a155743/scripts/verify-plugins.mjs" in text
    assert "Code-only" in text or "code-only" in text
    assert "Local-only" in text or "local" in text.lower()
    assert "network" in text.lower()
    assert "collision" in text.lower()
