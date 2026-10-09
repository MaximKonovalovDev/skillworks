"""Steal suggest: clap-style did-you-mean (cutoff 0.7)."""
from click.testing import CliRunner

from book2skill.cli import main


def test_mak_suggests_make():
    result = CliRunner().invoke(main, ["mak"])
    assert "Did you mean 'make'?" in result.output, result.output


def test_extarct_suggests_extract():
    result = CliRunner().invoke(main, ["extarct"])
    assert "Did you mean 'extract'?" in result.output, result.output


def test_unrelated_suggests_nothing():
    result = CliRunner().invoke(main, ["zzzzzz"])
    assert "Did you mean" not in result.output, result.output

