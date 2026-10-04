"""One source for the four copies of scripts/run_pairs.py.

    python tools/gen_run_pairs.py            # rewrite every copy from tools/run_pairs.tmpl (prints what changed)
    python tools/gen_run_pairs.py --check    # exit 1 when a copy differs from what the source makes (drift)
    python tools/gen_run_pairs.py --root DIR # another repo root (the tests use a scratch one)

engine-builder, edit-reread, repo-read-first and pwsh-for-bash-writers each ship a `scripts/run_pairs.py` that replays the
bad/good pairs of their `references/pairs.json` in pwsh 7. The four were copies by hand (114 of 128 lines the same). A
skill folder must still work when it is copied alone into another repo, so the copies cannot import one shared module
from tools/; they stay four files and are generated from the one source, `tools/run_pairs.tmpl`. Edit that file (the
shared code, once) or the VARIANTS table below (what differs per skill), then run this tool.

The template is the code with whole-line markers `#@if <flag>`, `#@else`, `#@end` and slots `{{name}}`. The files are
written byte for byte as they were before (no "generated" banner: a skill's live-proof fingerprint covers its files, so a
changed byte would void the proof of a shipped skill), and `tests/test_gen_run_pairs.py` fails when a copy drifts.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TEMPLATE = HERE / "run_pairs.tmpl"

# skill -> flags that switch template blocks on, and the slot values. `skill` is filled from the key.
VARIANTS: dict[str, dict] = {
    "engine-builder": {"flags": set(), "vars": {"tag": "eb", "bad_line": "no-edit", "good_report": "landed or claimed", "one_line": "one line per pair"}},
    "edit-reread": {"flags": set(), "vars": {"tag": "er", "bad_line": "stale-edit", "good_report": "reread-first", "one_line": "one line per pair"}},
    "repo-read-first": {"flags": set(), "vars": {"tag": "rr", "bad_line": "guessed-read", "good_report": "check-first", "one_line": "one line per pair"}},
    # strip: one pwsh run with Git's usr/bin out of PATH (grep, head, wc, sed fail), and pairs whose tools are missing are skipped
    "pwsh-for-bash-writers": {"flags": {"strip"}, "vars": {"one_line": "prints one line per pair"}},
}
SLOT = re.compile(r"\{\{(\w+)\}\}")


def render(skill: str, template: str | None = None) -> str:
    """The text of skills/<skill>/scripts/run_pairs.py made from the template."""
    spec = VARIANTS[skill]
    values = {"skill": skill, **spec["vars"]}
    out: list[str] = []
    stack: list[bool] = []  # one entry per open #@if: is its current branch on
    for line in (template if template is not None else TEMPLATE.read_text(encoding="utf-8")).split("\n"):
        word = line.strip()
        if word.startswith("#@if "):
            stack.append(word[5:].strip() in spec["flags"])
        elif word == "#@else":
            stack[-1] = not stack[-1]
        elif word == "#@end":
            stack.pop()
        elif all(stack):
            out.append(SLOT.sub(lambda m: values[m.group(1)], line))
    if stack:
        raise ValueError("an #@if has no #@end in the template")
    return "\n".join(out)


def target(root: Path, skill: str) -> Path:
    return root / "skills" / skill / "scripts" / "run_pairs.py"


def drifted(root: Path) -> list[str]:
    """Skills whose copy is missing or differs from what the template makes (line ends ignored, so a CRLF checkout is not drift)."""
    bad = []
    for skill in VARIANTS:
        path = target(root, skill)
        if not path.is_file() or path.read_bytes().replace(b"\r\n", b"\n") != render(skill).encode("utf-8"):
            bad.append(skill)
    return bad


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="only compare; exit 1 when a copy differs from the source")
    ap.add_argument("--root", default=str(ROOT), help="repo root holding skills/ (default: this repo)")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    bad = drifted(root)
    if args.check:
        for skill in VARIANTS:
            print(f"{'DRIFT' if skill in bad else 'ok   '} {skill}: skills/{skill}/scripts/run_pairs.py"
                  + (" differs from tools/run_pairs.tmpl; edit the template, then python tools/gen_run_pairs.py" if skill in bad else ""))
        return 1 if bad else 0
    for skill in VARIANTS:
        if skill in bad:
            path = target(root, skill)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(render(skill), encoding="utf-8", newline="\n")
        print(f"{'updated' if skill in bad else 'current'} {skill}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
