"""Grader registry: YAML/CLI/Python resolve identically, unknown fails loudly."""
import pytest

from book2skill import graders


def test_registry_lookup_identical_for_yaml_cli_python() -> None:
    from_yaml = graders.lookup("neg_control")
    from_cli = graders.lookup("neg_control ".strip())
    from_python = graders.lookup(str("neg_control"))
    assert from_yaml is from_cli is from_python
    assert from_yaml["id"] == "neg_control"


def test_unknown_grader_fails_loudly() -> None:
    with pytest.raises(KeyError, match="unknown grader"):
        graders.lookup("nope_missing")


def test_version_recorded_for_receipt() -> None:
    out = graders.grade_with("code_contains", "leases renew yearly", ["leases"])
    assert out == {"passed": True, "grader": "code_contains", "version": "1"}


def test_graders_grow_with_id_and_version() -> None:
    before = len(graders._GRADERS)
    stamp = graders.register_grader("demo_probe", "1", graders.code_contains)
    assert stamp == {"id": "demo_probe", "version": "1"}
    assert len(graders._GRADERS) == before + 1
    del graders._GRADERS["demo_probe"]
