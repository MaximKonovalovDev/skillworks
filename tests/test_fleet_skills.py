"""Fleet skills: format, sources, forge-safe English and the pipeline's eval gate, one run per skill.

The skills' executable examples are tested in each skill's own test file.
A skill that is not built yet is skipped, never faked.
"""
import pytest

import live_proof
import skill_gates as g


def _built(name: str) -> bool:
    return (g.SKILLS / name / "SKILL.md").is_file()


@pytest.mark.parametrize("name", sorted(g.FLEET_SKILLS))
def test_fleet_skill_format(name: str) -> None:
    if not _built(name):
        pytest.skip(f"{name} not built yet")
    g.check_format(name)


def test_frontmatter_folds_folded_description_scalar() -> None:
    """O-008: gates.frontmatter must fold `description: >-` like audit does."""
    text = ("---\nname: demo-skill\nlicense: MIT\ndescription: >-\n"
            "  Use when chaining commands in PowerShell for testing folded gates "
            "with enough characters to clear the length gate.\n---\nbody\n")
    desc = g.frontmatter(text).get("description", "")
    assert len(desc) > 40
    assert desc.startswith("Use when")
    assert ">-" not in desc
    g.check_format("git-one-branch")


def test_gates_frontmatter_reads_git_one_branch_folded_description() -> None:
    """Repair: gates.frontmatter must fold the shipped git-one-branch `>-` scalar (477 chars, not 2)."""
    text = (g.SKILLS / "git-one-branch" / "SKILL.md").read_text(encoding="utf-8")
    desc = g.frontmatter(text).get("description", "")
    assert len(desc) > 40, f"git-one-branch description is {len(desc)} chars, want 40-1024"
    assert desc.startswith("Use before")
    assert ">-" not in desc


@pytest.mark.parametrize("name", sorted(g.FLEET_SKILLS))
def test_fleet_skill_sources_and_notices(name: str) -> None:
    if not _built(name):
        pytest.skip(f"{name} not built yet")
    g.check_sources(name)


@pytest.mark.parametrize("name", sorted(g.FLEET_SKILLS))
def test_fleet_skill_eval_gate(name: str) -> None:
    if not _built(name):
        pytest.skip(f"{name} not built yet")
    assert g.check_eval(name) >= g.EVAL_GATE


@pytest.mark.parametrize("name", sorted(g.FLEET_SKILLS))
def test_fleet_skill_matches_its_last_live_proof(name: str) -> None:
    """Edited a skill, its QA file or its tests? Run `python tests/live_proof.py <name>` again."""
    if not _built(name):
        pytest.skip(f"{name} not built yet")
    g.check_proof(name)


def test_reseal_keeps_a_fresh_seal() -> None:
    """big22: a re-run with the same fingerprint and result must not rewrite the proof (else the zip re-stales)."""
    assert live_proof.same_seal({"fingerprint": "abc", "result": "3 passed in 1.00s"}, "abc", "3 passed in 1.00s")


def test_reseal_rewrites_a_changed_skill() -> None:
    """big22: a changed fingerprint (or a new result) still reseals, so the bar does not move."""
    assert not live_proof.same_seal({"fingerprint": "abc", "result": "3 passed in 1.00s"}, "def", "3 passed in 1.00s")
    assert not live_proof.same_seal({"fingerprint": "abc", "result": "3 passed in 1.00s"}, "abc", "4 passed in 1.00s")
    assert not live_proof.same_seal({}, "abc", "3 passed in 1.00s")
