"""book2skill CLI: make (all in one) | extract | split | index | build | audit | eval | refresh | export."""
from __future__ import annotations

from pathlib import Path

import click

from . import audit as audit_mod
from . import build as build_mod
from . import distill as distill_mod
from . import eval as eval_mod
from . import export as export_mod
from . import extract as extract_mod
from . import index as index_mod
from . import make as make_mod
from . import refresh as refresh_mod


@click.group()
def main() -> None:
    """Books you own into Agent Skills."""


@main.command()
@click.option("--in", "src", required=True, help="PDF/EPUB/DOCX/MD/TXT/URL you own, or a docs folder")
@click.option("--out", "out", required=True, help="work dir, e.g. work/mybook")
@click.option("--glob", "include", default=None, help="docs folder only: file name or path pattern, e.g. 'about_*.md'")
@click.option("--engine", default="classic", type=click.Choice(["classic", "markitdown", "auto"]),
              help="classic keeps plain text; markitdown keeps headings, tables and code fences (PDF/EPUB/DOCX)")
def extract(src: str, out: str, include: str | None, engine: str) -> None:
    """Stage 1: source to text + metadata."""
    try:
        receipt = extract_mod.extract(src, Path(out), include=include, engine=engine)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from None
    counts = f"headings {receipt['md_headings']} tables {receipt['md_tables']} fences {receipt['md_fences']}"
    click.echo(f"extracted {receipt['chars']} chars ({receipt['kind']}, engine {receipt['engine']}; {counts})")


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
    try:
        receipt = build_mod.build(Path(work), Path(skill), name, description)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from None
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
@click.option("--target", required=True, type=click.Choice(export_mod.TARGETS),
              help="claude|codex|opencode|gemini")
@click.option("--out", required=True)
@click.option("--work", default=None, help="work dir to run eval inline, e.g. work/mybook")
@click.option("--qa", default=None, help="QA jsonl to run eval inline, e.g. evals/mybook_qa.jsonl")
@click.option("--eval-report", "eval_report_path", default=None, help="saved eval report JSON")
def export(skill: str, target: str, out: str, work: str | None, qa: str | None, eval_report_path: str | None) -> None:
    """Stage 8: copy skill to target layout."""
    import json

    eval_report: dict | None = None
    if eval_report_path:
        eval_report = json.loads(Path(eval_report_path).read_text(encoding="utf-8"))
    elif work or qa:
        if not (work and qa):
            raise click.UsageError("--work and --qa must be given together")
        eval_report = eval_mod.run_eval(Path(work), Path(skill), Path(qa))
    export_mod.export(Path(skill), target, Path(out), eval_report=eval_report)


@main.group()
def distill() -> None:
    """Distill kit (TS-2): reading packets and the cure-smith gate."""


@distill.command(name="plan")
@click.option("--work", required=True)
def distill_plan(work: str) -> None:
    """Group work/chunks into reading packets of at most 6000 tokens."""
    try:
        distill_mod.plan(Path(work))
    except ValueError as exc:
        raise click.UsageError(str(exc)) from None


@distill.command(name="check")
@click.option("--skill", required=True)
@click.option("--work", default=None, help="work dir whose chunks locators must resolve to")
def distill_check(skill: str, work: str | None) -> None:
    """Gate a distilled skill: budget, no scaffold, locators, pairs, ASCII."""
    report = distill_mod.check(Path(skill), Path(work) if work else None)
    if not report["ok"]:
        raise SystemExit(1)


@main.command()
@click.option("--in", "src", required=True, help="manual to learn from: a file, a docs folder or a URL you own")
@click.option("--name", required=True, help="skill name, a-z0-9- only; also the default work and skill folder")
@click.option("--description", required=True, help="what the skill does and when to use it (Use when ...)")
@click.option("--qa", required=True, help="QA jsonl: questions drawn from the failure the skill fixes")
@click.option("--work", default=None, help="work dir (default work/<name>)")
@click.option("--skill", default=None, help="skill dir (default skills/<name>)")
@click.option("--glob", "include", default=None, help="docs folder only: file name or path pattern, e.g. 'about_*.md'")
@click.option("--target", "targets", multiple=True, type=click.Choice(export_mod.TARGETS), help="also export (repeat for more)")
@click.option("--out", "out", default=None, help="export root (default dist)")
@click.option("--rebuild", is_flag=True, help="overwrite a SKILL.md an author already wrote")
@click.option("--engine", default="classic", type=click.Choice(["classic", "markitdown", "auto"]),
              help="extract engine: markitdown keeps headings, tables and code fences")
def make(src: str, name: str, description: str, qa: str, work: str | None, skill: str | None,
         include: str | None, targets: tuple[str, ...], out: str | None, rebuild: bool, engine: str) -> None:
    """One command: extract, split, index, build, eval, audit, and export when --target is given."""
    try:
        make_mod.make(src, name, description, Path(qa), work=work, skill=skill, include=include,
                      targets=targets, out=out, rebuild=rebuild, say=click.echo, engine=engine)
    except ValueError as exc:
        raise click.UsageError(str(exc)) from None


if __name__ == "__main__":
    main()
