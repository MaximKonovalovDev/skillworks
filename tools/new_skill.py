"""Stamp a new fleet skill from skills/_template, and check that no slot is left.

    python tools/new_skill.py <name> "<one-line description>" [--root DIR]
    python tools/new_skill.py --check <name> [--root DIR]

The first form writes the six files every fleet skill repeated by hand (the folder `skills/_template/` holds them):

    skills/<name>/SKILL.md                  front matter name, description, license; the "Use it" and "Rules" sections
    skills/<name>/references/sources.md     where the skill comes from, its licence, the verified date
    skills/<name>/scripts/<script>.py       argparse with --help, a work() to write, exits 2 until it is written
    tests/test_<script>.py                  the 3 stock tests (they call tests/skill_stock.py) and a place for yours
    evals/<name>_qa.jsonl                   the eval-gate rows: {"q", "must"}, a trigger row, must-literal rows
    evals/<name>_trials.jsonl               the stranger-run rows: {"id", "kind", "task", "must", "must_not"}

<script> is the name with hyphens made underscores (pipe-run -> pipe_run), the same rule `tests/skill_gates.py` uses to
find a skill's test file. Every thing left to write is a slot line, `{{slot: what to write}}`; the script prints
"ERROR not implemented" until work() is written. The tool refuses a bad name, a bad description and any skill that
already has one of the six files, and then writes nothing. It prints the slots still to fill and the next steps.

`--check <name>` prints each slot still open in the skill's files and exits 1 while one is left (0 when none).
`--root` is the repo root to stamp into (default: this repo); the templates always come from this repo.
Exit codes: 0 done, 1 `--check` found open slots, 2 refused or bad usage.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATES = ROOT / "skills" / "_template"

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")  # the folder rule of book2skill/build.py and tests/skill_gates.py
TRIGGER_RE = re.compile(r"\bUse (when|before|whenever|for)\b")  # the description rule of book2skill/gates.py check_format
SLOT_RE = re.compile(r"\{\{slot:\s*(.*?)\}\}")
LEFT_VARIABLE_RE = re.compile(r"\{\{(?!slot:)[^{}]*\}\}")
NOT_IMPLEMENTED = "ERROR not implemented: write work() in scripts/"
TEXT_SUFFIXES = {".md", ".py", ".json", ".jsonl", ".txt"}
SKIP_PARTS = {"export", "__pycache__", ".pytest_cache"}


def script_name(name: str) -> str:
    return name.replace("-", "_")


def targets(name: str, root: Path) -> list[tuple[str, Path]]:
    """(template file under skills/_template, file it is stamped to) for the six files of a skill."""
    script = script_name(name)
    return [
        ("SKILL.md", root / "skills" / name / "SKILL.md"),
        ("references/sources.md.tmpl", root / "skills" / name / "references" / "sources.md"),
        ("scripts/script.py.tmpl", root / "skills" / name / "scripts" / f"{script}.py"),
        ("tests/test_skill.py.tmpl", root / "tests" / f"test_{script}.py"),
        ("evals/qa.jsonl.tmpl", root / "evals" / f"{name}_qa.jsonl"),
        ("evals/trials.jsonl.tmpl", root / "evals" / f"{name}_trials.jsonl"),
    ]


def name_problem(name: str) -> str | None:
    if not NAME_RE.match(name) or len(name) > 64:
        return f"bad name {name!r}: use a-z, 0-9 and single hyphens, at most 64 characters (it is the folder name)"
    return None


def description_problem(description: str) -> str | None:
    if "\n" in description or "\r" in description:
        return "the description must be one line"
    if not 40 <= len(description) <= 1024:
        return f"the description is {len(description)} characters, want 40-1024"
    bad = sorted({c for c in description if ord(c) > 126})
    if bad:
        return f"the description has non-ASCII characters {bad[:5]}: the gates want plain ASCII"
    if not TRIGGER_RE.search(description):
        return "the description needs a trigger: say 'Use when ...', 'Use before ...', 'Use whenever ...' or 'Use for ...'"
    return None


def render(template: str, name: str, description: str, *, front_matter: bool) -> str:
    """The template text with the stamp variables filled; the {{slot: ...}} lines stay."""
    text = template.replace("{{name}}", name).replace("{{script}}", script_name(name)).replace("{{description_py}}", json.dumps(description))
    if front_matter:  # SKILL.md keeps its own front matter (the folder is a valid skill itself): swap name and description
        text = re.sub(r"(?m)^name:.*$", lambda m: f"name: {name}", text, count=1)
        text = re.sub(r"(?m)^description:.*$", lambda m: f"description: {description}", text, count=1)
    left = LEFT_VARIABLE_RE.findall(text)
    if left:
        raise ValueError(f"template variable not filled: {left[0]}")
    return text


def open_slots(path: Path) -> list[tuple[int, str]]:
    """(line number, what to write) for each slot or not-implemented marker in one text file."""
    found = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return found
    for n, line in enumerate(lines, 1):
        for m in SLOT_RE.finditer(line):
            found.append((n, m.group(1).strip()))
        if NOT_IMPLEMENTED in line:
            found.append((n, "the script still prints 'not implemented': write work() and delete that line"))
    return found


def skill_files(name: str, root: Path) -> list[Path]:
    """Every text file of a skill to scan: its folder, its test file, its QA and trial files."""
    base = root / "skills" / name
    script = script_name(name)
    files = [p for p in sorted(base.rglob("*")) if p.is_file() and p.suffix in TEXT_SUFFIXES and not (SKIP_PARTS & set(p.relative_to(base).parts))]
    files += [p for p in (root / "tests" / f"test_{script}.py", root / "evals" / f"{name}_qa.jsonl", root / "evals" / f"{name}_trials.jsonl") if p.is_file()]
    return files


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def stamp(name: str, description: str, root: Path) -> list[Path]:
    """Write the six files; returns them. Raises ValueError (nothing written) on a bad name, description or an existing file."""
    problem = name_problem(name) or description_problem(description)
    if problem:
        raise ValueError(problem)
    pairs = targets(name, root)
    taken = [rel(dest, root) for _, dest in pairs if dest.exists()]
    if taken:
        raise ValueError(f"{name} already has {', '.join(taken)}; nothing written (stamp a new name, or edit the files by hand)")
    rendered = []
    for template, dest in pairs:
        src = TEMPLATES / template
        if not src.is_file():
            raise ValueError(f"template missing: skills/_template/{template}")
        rendered.append((dest, render(src.read_text(encoding="utf-8"), name, description, front_matter=template == "SKILL.md")))
    for dest, text in rendered:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(text, encoding="utf-8", newline="\n")
    return [dest for dest, _ in rendered]


def print_slots(name: str, root: Path, files: list[Path]) -> int:
    count = 0
    for path in files:
        for n, what in open_slots(path):
            count += 1
            print(f"OPEN {rel(path, root)}:{n}: {what[:140]}")
    return count


def cmd_stamp(name: str, description: str, root: Path) -> int:
    try:
        written = stamp(name, description, root)
    except ValueError as err:
        print(f"ERROR refused: {err}")
        return 2
    print(f"STAMPED {name}: {len(written)} files")
    for path in written:
        print(f"  {rel(path, root)}")
    n = print_slots(name, root, written)
    script = script_name(name)
    print(f"{n} slots to fill (python tools/new_skill.py --check {name} lists them again). Next:")
    print(f"  1. fill every slot; write the real work in work() of skills/{name}/scripts/{script}.py")
    print(f"  2. add \"{name}\": [] to FLEET_SKILLS in book2skill/gates.py ([] = original work; a source needs its credit text)")
    print(f"  3. python -m pytest tests/test_{script}.py -q")
    print(f"  4. python tools/new_skill.py --check {name}   (exit 0 when no slot is left)")
    print(f"  5. python tests/live_proof.py {name}   (writes references/live-proof.json)")
    return 0


def cmd_check(name: str, root: Path) -> int:
    problem = name_problem(name)
    if problem:
        print(f"ERROR {problem}")
        return 2
    if not (root / "skills" / name).is_dir():
        print(f"ERROR no skill {name} under {root / 'skills'}")
        return 2
    files = skill_files(name, root)
    n = print_slots(name, root, files)
    if n:
        print(f"RESULT OPEN: {name} has {n} slots still to fill in {len(files)} files")
        return 1
    print(f"RESULT DONE: {name} has no slot left in {len(files)} files")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("name", help="skill name: a-z, 0-9 and hyphens (the folder under skills/)")
    ap.add_argument("description", nargs="?", help='one line, 40-1024 ASCII characters, with a trigger: "... Use when ..."')
    ap.add_argument("--check", action="store_true", help="list the slots still open in <name>; exit 1 while one is left")
    ap.add_argument("--root", default=str(ROOT), help="repo root to stamp into or check (default: this repo)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR refused: --root {root} is not a folder")
        return 2
    if args.check:
        if args.description is not None:
            ap.error("--check takes only the skill name")
        return cmd_check(args.name, root)
    if args.description is None:
        ap.error('give the description: python tools/new_skill.py <name> "<one-line description>"')
    return cmd_stamp(args.name, args.description, root)


if __name__ == "__main__":
    sys.exit(main())
