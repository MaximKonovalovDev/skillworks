"""make: one command from a manual (file, docs folder or URL) to a built, evaluated, audited skill.

extract, split, index, build, eval, audit, and export when a target is asked for. It chains the
stage functions and nothing else: no new rules except four refusals that stop a bad run early
(a name that breaks the rule, no QA file, work and skill dirs inside each other or inside the
source folder, and an export of a skill whose placeholder text nobody wrote over).
"""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path

from . import audit as audit_mod
from . import build as build_mod
from . import eval as eval_mod
from . import export as export_mod
from . import extract as extract_mod
from . import index as index_mod
from . import split as split_mod


def _inside(child: Path, parent: Path) -> bool:
    child, parent = child.resolve(), parent.resolve()
    return child == parent or parent in child.parents


def _check_places(src: str, work: Path, skill: Path) -> None:
    if _inside(work, skill) or _inside(skill, work):
        raise ValueError(f"--work {work} and --skill {skill} must not sit inside each other")
    if Path(src).is_dir():
        for label, place in (("--work", work), ("--skill", skill)):
            if _inside(place, Path(src)):
                raise ValueError(f"{label} {place} is inside the source folder {src}: the next run would read its own output")


def _quiet(fn, *args, **kwargs):
    """Run a stage that prints its own JSON report; make prints one line per stage instead."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


def make(src: str, name: str, description: str, qa: Path, work: Path | None = None,
         skill: Path | None = None, include: str | None = None, targets: tuple[str, ...] = (),
         out: Path | None = None, rebuild: bool = False, say=print, engine: str = "classic") -> dict:
    work = Path(work) if work else Path("work") / name
    skill = Path(skill) if skill else Path("skills") / name
    out = Path(out) if out else Path("dist")
    build_mod.validate_name(name, skill)
    if not Path(qa).is_file():
        raise ValueError(f"--qa {qa} not found: write questions a person or agent drew from the failure this skill fixes, one JSON per line {{\"q\", \"must\"}}")
    eval_mod.validate_qa(Path(qa))
    _check_places(src, work, skill)

    result: dict = {"name": name, "source": src, "skill": str(skill), "work": str(work), "stages": {}}
    stages = result["stages"]

    stages["extract"] = extract_mod.extract(src, work, include=include, engine=engine)
    say(f"extract  {stages['extract']['kind']}, {stages['extract']['chars']} chars"
        + (f", {stages['extract']['files']} files" if "files" in stages["extract"] else ""))
    stages["split"] = split_mod.split(work)
    say(f"split    {stages['split']['chunks']} chunks")
    stages["index"] = index_mod.build_index(work)
    say(f"index    {stages['index']['records']} records")

    kept = (skill / "SKILL.md").is_file() and "SKILL.md" not in build_mod.scaffold_leftovers(skill)
    if kept and not rebuild:
        stages["build"] = {"stage": "build", "skipped": "SKILL.md was written by an author; --rebuild overwrites it"}
        say("build    skipped: SKILL.md already has an author (--rebuild overwrites it)")
    else:
        stages["build"] = build_mod.build(work, skill, name, description)
        say(f"build    {skill}")

    report = _quiet(eval_mod.run_eval, work, skill, Path(qa))
    stages["eval"] = {"total": report["total"], "passed": report["passed"], "rate": report["rate"]}
    say(f"eval     {report['passed']}/{report['total']} = {report['rate']:.3f} (gate {export_mod.GATE})")
    audit = _quiet(audit_mod.audit, skill)
    stages["audit"] = {"files": len(audit["sections"]), "total_tokens": audit["total_tokens"],
                       "body_tokens": audit.get("body_tokens"), "over_budget": audit.get("over_budget", False)}
    audit_line = f"audit    {len(audit['sections'])} files, {audit['total_tokens']} tokens"
    if audit.get("over_budget"):
        audit_line += f" (over budget: body {audit.get('body_tokens')} > {audit.get('body_budget')})"
    say(audit_line)

    left = build_mod.scaffold_leftovers(skill)
    result["placeholders"] = left
    say("fill     " + (", ".join(left) + " still hold the scaffold text (a person or agent writes them)" if left else "nothing left to write"))

    result["gate"] = "pass" if report["rate"] >= export_mod.GATE else "refused"
    if report["rate"] < export_mod.GATE:
        _write(work, result)
        raise SystemExit(f"eval gate refused: rate {report['rate']:.3f} below {export_mod.GATE:.1f}; fix the skill, not the test")
    if targets and left:
        _write(work, result)
        raise SystemExit("export held: " + ", ".join(left) + " still hold the scaffold text; write them first (a pack with placeholder text is not shipped)")
    stages["export"] = []
    for target in targets:
        receipt = _quiet(export_mod.export, skill, target, out, eval_report=report)
        stages["export"].append(receipt)
        say(f"export   {receipt['dest']}")
    _write(work, result)
    say(f"receipt  {work / 'make.json'}")
    return result


def _write(work: Path, result: dict) -> None:
    (work / "make.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
