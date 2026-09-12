"""book2skill CLI: extract | split | index | build | audit | eval | refresh | export."""
from __future__ import annotations

from pathlib import Path

import click

from . import audit as audit_mod
from . import build as build_mod
from . import eval as eval_mod
from . import export as export_mod
from . import extract as extract_mod
from . import index as index_mod
from . import refresh as refresh_mod


@click.group()
def main() -> None:
    """Books you own into Agent Skills."""


@main.command()
@click.option("--in", "src", required=True, help="PDF/EPUB/DOCX/MD/TXT/URL you own")
@click.option("--out", "out", required=True, help="work dir, e.g. work/mybook")
def extract(src: str, out: str) -> None:
    """Stage 1: source to text + metadata."""
    receipt = extract_mod.extract(src, Path(out))
    click.echo(f"extracted {receipt['chars']} chars ({receipt['kind']})")


@main.command()
@click.option("--work", required=True)
def split(work: str) -> None:
    """Stage 2: 5k-char chunks."""
    receipt = index_mod_split(work)
    click.echo(f"split into {receipt['chunks']} chunks")


def index_mod_split(work: str) -> dict:
    from . import split as split_mod

    return split_mod.split(Path(work))


@main.command(name="index")
@click.option("--work", required=True)
def index_cmd(work: str) -> None:
    """Stage 3: grounded JSONL index."""
    receipt = index_mod.build_index(Path(work))
    click.echo(f"indexed {receipt['records']} records")


@main.command()
@click.option("--work", required=True)
@click.option("--skill", required=True)
@click.option("--name", required=True)
@click.option("--description", required=True)
def build(work: str, skill: str, name: str, description: str) -> None:
    """Stage 4: notes-then-skill scaffold."""
    receipt = build_mod.build(Path(work), Path(skill), name, description)
    click.echo(f"built {receipt['skill']} ({receipt['note_chars']} note chars)")


@main.command()
@click.option("--skill", required=True)
def audit(skill: str) -> None:
    """Stage 5: token-cost report."""
    audit_mod.audit(Path(skill))


@main.command()
@click.option("--work", required=True)
@click.option("--skill", required=True)
@click.option("--qa", required=True)
def eval(work: str, skill: str, qa: str) -> None:
    """Stage 6: Q&A pass-rate gate."""
    eval_mod.run_eval(Path(work), Path(skill), Path(qa))


@main.command()
@click.option("--work", required=True)
def refresh(work: str) -> None:
    """Stage 7: fingerprint-locked reindex."""
    receipt = refresh_mod.refresh(Path(work))
    click.echo("changed, reindexed" if receipt["changed"] else "unchanged, no-op")


@main.command()
@click.option("--skill", required=True)
@click.option("--target", required=True, help="claude|codex|opencode|gemini")
@click.option("--out", required=True)
def export(skill: str, target: str, out: str) -> None:
    """Stage 8: copy skill to target layout."""
    export_mod.export(Path(skill), target, Path(out))


if __name__ == "__main__":
    main()
