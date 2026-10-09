"""Steal changelog bump + trust section: computed minimum bump replaces the manual slot; Trust carries badge+sha+scope+guard, never a slot."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pack_build as pb

PACK = {
    "slug": "fix-pack",
    "title": "Fix Pack",
    "version": "1.0.0",
    "price_usd": 9,
    "skills": [{"name": "alpha", "licence": "MIT", "credit": "own work"}],
    "vol0": {"name": "free-one", "licence": "CC-BY-4.0", "credit": "free"},
}


def test_commit_bump_parses_conventional_subjects():
    assert pb.commit_bump("feat: add a skill") == "minor"
    assert pb.commit_bump("feat(api): add a skill") == "minor"
    assert pb.commit_bump("fix: repair a path") == "patch"
    assert pb.commit_bump("docs: touch readme") == "patch"
    assert pb.commit_bump("feat!: drop old shape") == "major"
    assert pb.commit_bump("fix!: drop old shape") == "major"
    assert pb.commit_bump("feat: add\n\nBREAKING CHANGE: drop old shape") == "major"
    assert pb.commit_bump("random words") == "patch"
    assert pb.commit_bump("") == "patch"


def test_strongest_bump_wins_major_then_minor():
    assert pb.strongest_bump([]) == "patch"
    assert pb.strongest_bump(["fix: a"]) == "patch"
    assert pb.strongest_bump(["fix: a", "feat: b"]) == "minor"
    assert pb.strongest_bump(["feat: b", "fix: a", "feat!: c"]) == "major"
    assert pb.strongest_bump(["docs: d", "feat: b"]) == "minor"


def test_bump_version_and_minimum_guard():
    assert pb.bump_version("1.2.3", "patch") == "1.2.4"
    assert pb.bump_version("1.2.3", "minor") == "1.3.0"
    assert pb.bump_version("1.2.3", "major") == "2.0.0"
    assert pb.minimum_version("1.2.3", "minor") == "1.3.0"
    assert pb.meets_minimum_bump("1.2.3", "1.3.0", "minor") is True
    assert pb.meets_minimum_bump("1.2.3", "1.2.9", "minor") is False
    assert pb.meets_minimum_bump("1.2.3", "2.0.0", "major") is True
    assert pb.meets_minimum_bump("1.2.3", "1.9.9", "major") is False


def test_changelog_line_is_computed_keep_a_changelog_with_no_slot():
    line = pb.changelog_line("2026-10-09", "1.0.0", "minor")
    assert "2026-10-09" in line and "1.0.0" in line and "minor" in line
    assert "Keep a Changelog" in line
    assert pb.open_slots(line) == []


def test_trust_lines_carry_badge_sha_scope_guard_and_no_slot():
    lines = pb.trust_lines("fix-pack", "abc1234", ["alpha"])
    text = "\n".join(lines)
    assert pb.TRUST_BADGE in text and "code-verified" in text
    assert "abc1234" in text
    assert "fix-pack" in text and "not the whole catalog" in text
    assert "Collision guard" in text and "trust" in text.lower()
    assert pb.open_slots(text) == [], "trust is computed, never a catalog slot"
    try:
        pb.check_trust_collision(["alpha", "Trust"])
    except ValueError as err:
        assert "collides" in str(err)
    else:
        raise AssertionError("trust collision did not refuse")


def test_listing_starter_changelog_slot_1_to_0_and_trust_section_plus_1():
    assert len(pb.LISTING_SECTIONS) == 13, pb.LISTING_SECTIONS
    assert pb.LISTING_SECTIONS[-1] == ("Trust", None)
    listing = pb.listing_starter(PACK, ROOT / "skills", "2026-10-09", commits=["fix: a typo"], sha="deadbee")
    assert "\n## Trust\n" in listing and "\n## Changelog\n" in listing
    changelog = listing.split("## Changelog")[1].split("## Trust")[0]
    trust = listing.split("## Trust")[1]
    assert pb.open_slots(changelog) == [], "manual Changelog slot 1->0 with computed minimum bump"
    assert "minimum patch bump" in changelog
    assert pb.open_slots(trust) == []
    assert "deadbee" in trust and "code-verified" in trust
    feat_listing = pb.listing_starter(PACK, ROOT / "skills", "2026-10-09", commits=["feat: a skill"], sha="deadbee")
    assert "minimum minor bump" in feat_listing.split("## Changelog")[1].split("## Trust")[0]
    breaking = pb.listing_starter(PACK, ROOT / "skills", "2026-10-09", commits=["feat!: drop shape"], sha="deadbee")
    assert "minimum major bump" in breaking.split("## Changelog")[1].split("## Trust")[0]
    print("changelog slots 1->0, trust sections 0->1")
