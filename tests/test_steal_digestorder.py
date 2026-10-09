
"""Steal digest order: pinned expected over manifest over metadata, fail-closed require."""
import base64
import hashlib
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("install_fleet_skills", ROOT / "tools" / "install_fleet_skills.py")
inst = importlib.util.module_from_spec(spec)
sys.modules["install_fleet_skills"] = inst
spec.loader.exec_module(inst)

HEX_A = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
HEX_B = "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"
HEX_C = "3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d"
HEX_D = "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"


def _sri_for(hex_digest):
    raw = bytes.fromhex(hex_digest)
    return "sha256-" + base64.b64encode(raw).decode("ascii")


def test_digest_order_tuple():
    assert tuple(inst.DIGEST_ORDER) == ("expectedSha256", "files.zip.sha256", "sha256")
    print("digest-order: pinned")


def test_expected_wins_over_manifest_and_metadata():
    artifact = {"expectedSha256": HEX_A, "manifest": {"files.zip.sha256": HEX_B}, "metadata": {"sha256": HEX_C}}
    source, hexval = inst.pinned_digest(artifact)
    assert source == "expectedSha256"
    assert hexval == HEX_A
    print("expected-wins: 1")


def test_manifest_fallback_when_no_expected():
    artifact = {"manifest": {"files.zip.sha256": HEX_B}, "metadata": {"sha256": HEX_C}}
    source, hexval = inst.pinned_digest(artifact)
    assert source == "files.zip.sha256"
    assert hexval == HEX_B
    print("manifest-fallback: 1")


def test_metadata_sha256_when_no_higher_pin():
    artifact = {"metadata": {"sha256": HEX_C}}
    source, hexval = inst.pinned_digest(artifact)
    assert source == "sha256"
    assert hexval == HEX_C
    print("metadata-sha256: 1")


def test_metadata_sri_parsed_to_hex():
    sri = _sri_for(HEX_D)
    artifact = {"metadata": {"integrity": sri}}
    source, hexval = inst.pinned_digest(artifact)
    assert source == "sha256"
    assert hexval == HEX_D
    assert inst._sri_sha256_to_hex(sri) == HEX_D
    assert inst._sri_sha256_to_hex("sha384-abc") is None
    print("metadata-sri: 1")


def test_missing_digest_fail_closed():
    checks = inst.verify_artifact({"name": "demo"}, HEX_A, require_digest=True)
    assert len(checks) == 1
    check = checks[0]
    assert check["id"] == "digest-present"
    assert check["ok"] is False
    assert check["level"] == "error"
    print("missing-fail-closed: 1")


def test_missing_digest_allowed_when_not_required():
    checks = inst.verify_artifact({"name": "demo"}, HEX_A, require_digest=False)
    assert len(checks) == 1
    assert checks[0]["id"] == "digest-present"
    assert checks[0]["ok"] is True
    print("missing-allowed: 1")


def test_match_pass_and_mismatch_fail():
    good = {"expectedSha256": HEX_A}
    checks = inst.verify_artifact(good, HEX_A)
    assert checks[0]["id"] == "digest-match"
    assert checks[0]["ok"] is True
    upper = inst.verify_artifact({"expectedSha256": HEX_A.upper()}, HEX_A)
    assert upper[0]["ok"] is True
    bad = inst.verify_artifact(good, HEX_B)
    assert bad[0]["id"] == "digest-match"
    assert bad[0]["ok"] is False
    assert bad[0]["level"] == "error"
    assert bad[0]["expected"] == HEX_A
    assert bad[0]["actual"] == HEX_B
    print("match-mismatch: 1")


def test_checks_schema():
    groups = [inst.verify_artifact({}, HEX_A), inst.verify_artifact({"expectedSha256": HEX_A}, HEX_A)]
    groups.append(inst.verify_artifact({"expectedSha256": HEX_A}, HEX_B))
    for checks in groups:
        assert len(checks) == 1
        for key in ("id", "ok", "level", "title", "summary", "remediation", "expected", "actual"):
            assert key in checks[0]
    print("checks-schema: 1")


def test_unverified_paths_one_to_zero():
    artifacts = [{"name": "b", "expectedSha256": HEX_A}, {"name": "a"}]
    assert inst.unverified_install_paths(artifacts) == ["a"]
    fixed = [{"name": "b", "expectedSha256": HEX_A}, {"name": "a", "manifest": {"files.zip.sha256": HEX_B}}]
    assert inst.unverified_install_paths(fixed) == []
    assert inst.unverified_install_paths(artifacts, require_digest=False) == []
    print("unverified-1-to-0: 1")


def test_attribution_present():
    text = (ROOT / "tools" / "install_fleet_skills.py").read_text(encoding="utf-8")
    assert "extensiondev/artifact-integrity" in text
    assert "Apache-2.0" in text
    assert "https://github.com/extensiondev/artifact-integrity" in text
    assert "no donor code copied" in text.lower()
    print("attribution: 1")
