"""Legal book supply: Bevy plus docs slice manifest (BK-1005-2, R4).

Own original work, stdlib only. Each slice is small (a few files), maps to
one fleet failure class, names a sellable licence, and lands under work/
(which is git-ignored, never committed). NC/SA/AGPL sources are never sold:
code refuses them before anything is written.

    python tools/legal_supply_bevy.py manifest
    python tools/legal_supply_bevy.py check
    python tools/legal_supply_bevy.py sheet --out evals/bevy-docs_trials.jsonl

Licence notes (read live via `gh api repos/<repo>`, pinned refs below):
- bevyengine/bevy engine text: Apache-2.0 OR MIT (dual).
- bevy cheatbook code samples: MIT-0.
- microsoft/playwright docs: CC-BY-4.0 text.
- MicrosoftDocs/PowerShell-Docs prose: CC-BY-4.0; its code samples: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WORK_DIR = ROOT / "work" / "legal-supply-bevy"

# One fleet failure class per slice (the families tools/fleet_failures.py counts).
FAILURE_CLASSES = ("bevy", "browser", "pwsh", "git")

SLICES: list[dict] = [
    {
        "id": "bevy-engine",
        "repo": "bevyengine/bevy",
        "ref": "v0.19.1",
        "pin": "b56fc29d3016e641754765244b5ba3f9cc504671",
        "license_spdx": "Apache-2.0 OR MIT",
        "license_note": "engine dual licence; own words and own code only",
        "failure_class": "bevy",
        "files": ["crates/bevy_ecs/README.md", "crates/bevy_app/README.md"],
    },
    {
        "id": "bevy-cheatbook-code",
        "repo": "bevy-cheatbook/bevy-cheatbook",
        "ref": "main",
        "pin": "live",
        "license_spdx": "MIT-0",
        "license_note": "cheatbook code samples; short quotes only",
        "failure_class": "bevy",
        "files": ["src/code/bundles.md", "src/code/setup.md"],
    },
    {
        "id": "playwright-docs",
        "repo": "microsoft/playwright",
        "ref": "v1.63.0",
        "pin": "1b025d7",
        "license_spdx": "CC-BY-4.0",
        "license_note": "docs text; ideas only, rewritten",
        "failure_class": "browser",
        "files": ["docs/src/locators.md", "docs/src/auto-waiting.md"],
    },
    {
        "id": "pwsh-docs-text",
        "repo": "MicrosoftDocs/PowerShell-Docs",
        "ref": "main",
        "pin": "a3de8f2",
        "license_spdx": "CC-BY-4.0",
        "license_note": "prose; rewritten in our own words",
        "failure_class": "pwsh",
        "files": ["reference/docs-conceptual/about_Parsing.md"],
    },
    {
        "id": "pwsh-docs-code",
        "repo": "MicrosoftDocs/PowerShell-Docs",
        "ref": "main",
        "pin": "a3de8f2",
        "license_spdx": "MIT",
        "license_note": "code samples only; every example re-run",
        "failure_class": "pwsh",
        "files": ["reference/docs-conceptual/samples/Parsing.md"],
    },
]

MAX_FILES_PER_SLICE = 3

# Anything with these tokens is never sold. Word-boundary match so that
# "MIT" never trips "NC"/"SA" and "CC-BY-4.0" stays sellable.
_REFUSED = re.compile(r"\b(NC|SA|NONCOMMERCIAL|SHAREALIKE)\b|AGPL|GPL|SSPL|GFDL|NOASSERTION", re.I)


def is_sellable(spdx: str) -> bool:
    """True when a licence may be sold. NC, SA, AGPL (and GPL family) never."""
    text = str(spdx or "").strip()
    if not text:
        return False
    return not _REFUSED.search(text)


def ensure_work_path(path: Path | str) -> Path:
    """Sources land under work/ only (work/ is git-ignored). Refuse the rest."""
    dest = (ROOT / str(path)).resolve() if not Path(str(path)).is_absolute() else Path(str(path)).resolve()
    try:
        dest.relative_to(ROOT / "work")
    except ValueError:
        raise ValueError(f"refused: sources stay in work/, got {path}")
    return dest


def dest_for(slice_id: str) -> Path:
    return ensure_work_path(WORK_DIR / slice_id)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_slice(s: dict) -> list[str]:
    problems: list[str] = []
    if s.get("failure_class") not in FAILURE_CLASSES:
        problems.append(f"{s.get('id')}: failure_class must be one of {FAILURE_CLASSES}")
    if not is_sellable(str(s.get("license_spdx", ""))):
        problems.append(f"{s.get('id')}: licence {s.get('license_spdx')!r} is never sold (NC/SA/AGPL)")
    files = s.get("files", [])
    if not 1 <= len(files) <= MAX_FILES_PER_SLICE:
        problems.append(f"{s.get('id')}: keep the slice small (1-{MAX_FILES_PER_SLICE} files, has {len(files)})")
    try:
        dest_for(str(s.get("id")))
    except ValueError as exc:
        problems.append(str(exc))
    for key in ("repo", "ref", "license_spdx"):
        if not s.get(key):
            problems.append(f"{s.get('id')}: {key} is missing")
    return problems


def check_all(slices: list[dict] | None = None) -> list[str]:
    out: list[str] = []
    for s in slices or SLICES:
        out.extend(check_slice(s))
    ids = [s.get("id") for s in slices or SLICES]
    if len(set(ids)) != len(ids):
        out.append("duplicate slice id")
    return out


def read_license_live(repo: str) -> dict:
    """Read the licence live from GitHub. Network only when called."""
    r = subprocess.run(
        ["gh", "api", f"repos/{repo}", "--jq", "{spdx: .license.spdx_id, name: .license.name}"],
        capture_output=True, text=True, timeout=60, cwd=ROOT,
    )
    if r.returncode != 0:
        raise RuntimeError(f"cannot read licence for {repo}: {r.stderr.strip()[:120]}")
    try:
        doc = json.loads(r.stdout)
    except ValueError as exc:
        raise RuntimeError(f"bad licence JSON for {repo}: {exc}") from exc
    spdx = str(doc.get("spdx") or "NOASSERTION")
    if not is_sellable(spdx):
        raise RuntimeError(f"refused: {repo} licence {spdx!r} is never sold")
    return {"repo": repo, "spdx": spdx, "name": doc.get("name", "")}


def record_fetch(slice_id: str, content: bytes, commit_sha: str, license_spdx: str) -> dict:
    """Store one fetched slice under work/ with its SHA and live licence.

    Refuses NC/SA/AGPL before writing anything. Returns the receipt.
    """
    if not is_sellable(license_spdx):
        raise ValueError(f"refused: {slice_id} licence {license_spdx!r} is never sold")
    dest = dest_for(slice_id)
    dest.mkdir(parents=True, exist_ok=True)
    digest = sha256_bytes(content)
    (dest / "source.bin").write_bytes(content)
    receipt = {
        "slice": slice_id,
        "sha256": digest,
        "commit": commit_sha,
        "license_spdx": license_spdx,
        "license_read": "live",
    }
    (dest / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


TASKS: list[dict] = [
    {"id": "bb-01", "slice": "bevy-engine", "kind": "answer",
     "task": "A Bevy 0.19 app panics on add_systems(Update, foo) with a schedule error. Which plugin must be added first and what does the MinimalPlugins plus DefaultPlugins split change?",
     "must": ["App", "DefaultPlugins", "MinimalPlugins"], "must_not": [],
     "locator": "crates/bevy_app/README.md@v0.19.1 ECS schedule"},
    {"id": "bb-02", "slice": "bevy-engine", "kind": "answer",
     "task": "Name the two observer parameters in Bevy 0.19 and state why Trigger<T> no longer appears as one.",
     "must": ["On", "observer"], "must_not": ["Trigger<"],
     "locator": "crates/bevy_ecs/README.md@v0.19.1 observers"},
    {"id": "bb-03", "slice": "bevy-engine", "kind": "run",
     "task": "Run the sim-outside-bevy checker on a crate that depends on bevy 0.19. Paste the FAIL line naming the bevy dependency.",
     "must": ["FAIL", "bevy"], "must_not": ["no bevy dependency"],
     "locator": "crates/bevy_ecs/README.md@v0.19.1 sim check", "exit": 1},
    {"id": "bb-04", "slice": "bevy-cheatbook-code", "kind": "answer",
     "task": "State the cheatbook rule for spawning a PbrBundle-style mesh in 0.19 without the removed bundle name, in your own words.",
     "must": ["spawn", "bundle"], "must_not": ["PbrBundle"],
     "locator": "src/code/bundles.md@main bundles"},
    {"id": "bb-05", "slice": "bevy-cheatbook-code", "kind": "answer",
     "task": "What setup order does the cheatbook give for a new 2D scene: camera first or entities first, and why?",
     "must": ["camera"], "must_not": [],
     "locator": "src/code/setup.md@main setup"},
    {"id": "bb-06", "slice": "playwright-docs", "kind": "answer",
     "task": "A Playwright click fails before the element is ready. Which locator-first rule plus auto-waiting behaviour fixes it without a sleep?",
     "must": ["locator", "auto-waiting"], "must_not": ["sleep"],
     "locator": "docs/src/locators.md@v1.63.0 locators"},
    {"id": "bb-07", "slice": "playwright-docs", "kind": "answer",
     "task": "State the context-isolation rule: what does each test get and what must never leak between tests?",
     "must": ["context", "isolation"], "must_not": [],
     "locator": "docs/src/auto-waiting.md@v1.63.0 isolation"},
    {"id": "bb-08", "slice": "playwright-docs", "kind": "run",
     "task": "Route one request with page.route and abort image loads. Paste the route line and the exit code.",
     "must": ["route", "abort"], "must_not": [],
     "locator": "docs/src/locators.md@v1.63.0 routing", "exit": 0},
    {"id": "bb-09", "slice": "pwsh-docs-text", "kind": "answer",
     "task": "PowerShell parses `date -u` as a cmdlet call and fails. What is the correct Get-Date form and why does the bash flag fail?",
     "must": ["Get-Date", "cmdlet"], "must_not": [],
     "locator": "reference/docs-conceptual/about_Parsing.md@main parsing"},
    {"id": "bb-10", "slice": "pwsh-docs-text", "kind": "answer",
     "task": "State the about_Parsing rule for quoting a path with spaces plus the exit-code variable to read after a native call.",
     "must": ["quote", "$LASTEXITCODE"], "must_not": ["$? alone"],
     "locator": "reference/docs-conceptual/about_Parsing.md@main quoting"},
    {"id": "bb-11", "slice": "pwsh-docs-code", "kind": "run",
     "task": "Run the MIT parsing sample that lists a folder with spaces in its name. Paste the two lines of output and the exit code.",
     "must": ["Get-ChildItem"], "must_not": ["is not recognized"],
     "locator": "reference/docs-conceptual/samples/Parsing.md@main sample", "exit": 0},
    {"id": "bb-12", "slice": "pwsh-docs-code", "kind": "run",
     "task": "Chain two commands with && in pwsh and show the second runs only on success. Paste the chain line and the exit code.",
     "must": ["&&"], "must_not": ["2>/dev/null"],
     "locator": "reference/docs-conceptual/samples/Parsing.md@main chain", "exit": 0},
]


def emit_sheet(out: Path | None = None) -> list[dict]:
    rows: list[dict] = []
    for t in TASKS:
        row = {"id": t["id"], "kind": t["kind"], "task": t["task"],
               "must": t["must"], "must_not": t["must_not"],
               "locator": t["locator"], "source_only": True}
        if t["kind"] == "run":
            row["exit"] = t.get("exit", 0)
            row["run"] = t["task"].split(".")[0][:60]
        else:
            row["run"] = None
        rows.append(row)
    if out is not None:
        out = ensure_work_path(out) if str(out).startswith("work/") else Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text("\n".join(json.dumps(r, ensure_ascii=True) for r in rows) + "\n", encoding="utf-8")
    return rows


def cmd_manifest(args: argparse.Namespace) -> int:
    if args.out:
        Path(args.out).write_text(json.dumps(SLICES, indent=2) + "\n", encoding="utf-8")
        print(f"manifest {len(SLICES)} slices -> {args.out}")
    else:
        print(json.dumps(SLICES, indent=2))
    return 0


def cmd_check(_args: argparse.Namespace) -> int:
    problems = check_all()
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        print(f"RESULT FAIL: {len(problems)} problems")
        return 1
    print(f"RESULT PASS: {len(SLICES)} slices, each small, sellable, mapped, under work/")
    return 0


def cmd_sheet(args: argparse.Namespace) -> int:
    rows = emit_sheet(Path(args.out) if args.out else None)
    kinds = sum(1 for r in rows if r["kind"] == "run")
    print(f"sheet {len(rows)} tasks (run {kinds}, answer {len(rows) - kinds})")
    if args.out:
        print(f"wrote {args.out}")
    print("RESULT PASS" if len(rows) == 12 else "RESULT FAIL")
    return 0 if len(rows) == 12 else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("manifest", help="print the slice manifest")
    m.add_argument("--out", default=None)
    m.set_defaults(fn=cmd_manifest)
    c = sub.add_parser("check", help="refuse NC/SA/AGPL, verify small slices under work/")
    c.set_defaults(fn=cmd_check)
    s = sub.add_parser("sheet", help="emit the 12-task sheet")
    s.add_argument("--out", default=None)
    s.set_defaults(fn=cmd_sheet)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
