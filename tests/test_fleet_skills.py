"""Fleet skills: format, sources, forge-safe English and the pipeline's eval gate, one run per skill.

The skills' executable examples are tested in each skill's own test file.
A skill that is not built yet is skipped, never faked.
"""
import pytest

import skill_gates as g


def _built(name: str) -> bool:
    return (g.SKILLS / name / "SKILL.md").is_file()


@pytest.mark.parametrize("name", sorted(g.FLEET_SKILLS))
def test_fleet_skill_format(name: str) -> None:
    if not _built(name):
        pytest.skip(f"{name} not built yet")
    g.check_format(name)


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
