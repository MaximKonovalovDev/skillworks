"""book-to-skill: every command, output line, exit code and refusal of SKILL.md and references/stages.md run for real.

Each test starts `python tools/b2s.py ...` as a subprocess (stdin closed) from a scratch project folder, the way an agent
in another repo would. Fast tests run always; the `live` one drives it through pwsh from a folder with spaces.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

import skill_gates as g
from skill_gates import live

ROOT = g.ROOT
SKILL = g.SKILLS / "book-to-skill"
B2S = ROOT / "tools" / "b2s.py"
pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")

QA = (
    '{"q": "how do I chain commands in Windows PowerShell 5.1?", "must": ["semicolon"]}\n'
    '{"q": "which operator exists only in PowerShell 7?", "must": ["operator"]}\n'
    '{"q": "what does a pipeline pass between commands?", "must": ["objects"]}\n'
)
PLACEHOLDERS = "SKILL.md, glossary.md, patterns.md, cheatsheet.md"


def b2s(cwd: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(B2S), *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", stdin=subprocess.DEVNULL, timeout=120)


@pytest.fixture()
def project(tmp_path: Path) -> Path:
    """A scratch project: a docs folder with decoys that must be left out, and a QA file."""
    docs = tmp_path / "manual"
    (docs / "sub").mkdir(parents=True)
    (docs / ".git").mkdir()
    (docs / "node_modules" / "pkg").mkdir(parents=True)
    (docs / "export" / "claude").mkdir(parents=True)
    (docs / "chain.md").write_text(
        "---\ntitle: Chaining\n---\n# Chaining\n\nUse a semicolon to chain commands in Windows PowerShell 5.1. "
        "The && operator exists only in PowerShell 7.\n", encoding="utf-8")
    (docs / "sub" / "pipe.md").write_text("A pipeline passes objects, not text.\n", encoding="utf-8")
    (docs / "notes.png").write_bytes(b"\x89PNG not a doc")
    (docs / ".git" / "hidden.md").write_text("hidden-secret-word\n", encoding="utf-8")
    (docs / "node_modules" / "pkg" / "readme.md").write_text("vendored-word\n", encoding="utf-8")
    (docs / "export" / "claude" / "old.md").write_text("stale-export-word\n", encoding="utf-8")
    (tmp_path / "qa.jsonl").write_text(QA, encoding="utf-8")
    return tmp_path


def make_args(*extra: str, name: str = "demo-skill") -> list[str]:
    return ["make", "--in", "manual", "--name", name, "--description", "Use when chaining commands in PowerShell.", "--qa", "qa.jsonl", *extra]


def write_the_skill(skill: Path) -> None:
    (skill / "SKILL.md").write_text(
        "---\nname: demo-skill\ndescription: Use when chaining commands in PowerShell.\nlicense: MIT\n---\nChain with a semicolon in 5.1.\n", encoding="utf-8")
    for fname in ("glossary.md", "patterns.md", "cheatsheet.md"):
        (skill / fname).write_text(f"# {fname}\n\nwritten by hand\n", encoding="utf-8")


@live
def test_make_prints_the_documented_lines_and_keeps_its_output_in_the_folder_you_stand_in(project: Path) -> None:
    r = b2s(project, *make_args())
    assert r.returncode == 0, r.stdout + r.stderr
    lines = r.stdout.splitlines()
    shapes = [r"extract  folder, \d+ chars, 2 files", r"split    1 chunks", r"index    1 records", r"build    skills[\\/]demo-skill",
              r"eval     3/3 = 1\.000 \(gate 0\.6\)", r"audit    \d+ files, \d+ tokens",
              r"fill     " + re.escape(PLACEHOLDERS) + r" still hold the scaffold text \(a person or agent writes them\)",
              r"receipt  work[\\/]demo-skill[\\/]make\.json"]
    assert len(lines) == len(shapes), r.stdout
    for line, shape in zip(lines, shapes):
        assert re.fullmatch(shape, line), (line, shape)
    # the defaults are relative to where the command runs, never to the skillworks repo
    assert (project / "work" / "demo-skill" / "make.json").is_file() and (project / "skills" / "demo-skill" / "SKILL.md").is_file()
    assert not (ROOT / "work" / "demo-skill").exists() and not (ROOT / "skills" / "demo-skill").exists()
    assert not (project / "dist").exists(), "no --target, no export"
    made = json.loads((project / "work" / "demo-skill" / "make.json").read_text(encoding="utf-8"))
    assert made["gate"] == "pass" and made["placeholders"] == PLACEHOLDERS.split(", ")
    assert list(made["stages"]) == ["extract", "split", "index", "build", "eval", "audit", "export"] and made["stages"]["export"] == []
    text = (project / "work" / "demo-skill" / "full_text.txt").read_text(encoding="utf-8")
    assert "semicolon" in text and "passes objects" in text and "title: Chaining" not in text
    for gone in ("hidden-secret-word", "vendored-word", "stale-export-word", "PNG"):
        assert gone not in text, "hidden folders, node_modules, export folders and non-doc files are left out"


@live
def test_the_stage_commands_one_by_one(project: Path) -> None:
    (project / "big.txt").write_text("word " * 2400, encoding="utf-8")  # 12000 characters
    work, skill = "work/big", "skills/big"
    r = b2s(project, "extract", "--in", "big.txt", "--out", work)
    assert r.returncode == 0 and re.fullmatch(r"extracted \d+ chars \(text[^)]*\)", r.stdout.strip()), r.stdout + r.stderr
    assert b2s(project, "split", "--work", work).stdout.strip() == "split into 3 chunks"
    assert sorted(p.name for p in (project / work / "chunks").iterdir()) == ["0000.txt", "0001.txt", "0002.txt"]
    assert len((project / work / "chunks" / "0000.txt").read_text(encoding="utf-8")) == 5000, "5000 characters, 200 overlap"
    assert b2s(project, "index", "--work", work).stdout.strip() == "indexed 3 records"
    built = b2s(project, "build", "--work", work, "--skill", skill, "--name", "big", "--description", "Use when testing.")
    assert built.returncode == 0 and re.fullmatch(r"built skills[\\/]big \(\d+ note chars\)", built.stdout.strip()), built.stdout
    for rel in ("SKILL.md", "glossary.md", "patterns.md", "cheatsheet.md", "chapters/notes.md", "references/sources.md"):
        assert (project / skill / rel).is_file(), rel
    (project / "big_qa.jsonl").write_text('{"q": "what is the word", "must": ["word"]}\n', encoding="utf-8")
    ev = b2s(project, "eval", "--work", work, "--skill", skill, "--qa", "big_qa.jsonl")
    report = json.loads(ev.stdout)
    assert ev.returncode == 0 and (report["total"], report["passed"], report["rate"]) == (1, 1, 1.0)
    assert json.loads((project / skill / "eval_report.json").read_text(encoding="utf-8"))["rate"] == 1.0
    au = json.loads(b2s(project, "audit", "--skill", skill).stdout)
    assert au["total_tokens"] == sum(s["tokens"] for s in au["sections"]) and {s["file"] for s in au["sections"]} >= {"SKILL.md", "glossary.md"}
    assert b2s(project, "refresh", "--work", work).stdout.strip() == "changed, reindexed"
    assert b2s(project, "refresh", "--work", work).stdout.strip() == "unchanged, no-op"
    (project / work / "chunks" / "0000.txt").write_text("changed chunk", encoding="utf-8")
    assert b2s(project, "refresh", "--work", work).stdout.strip() == "changed, reindexed"


@live
def test_export_is_held_until_you_write_the_skill_then_the_zip_has_skill_md_at_its_root(project: Path) -> None:
    held = b2s(project, *make_args("--target", "claude", "--out", "dist"))
    assert held.returncode == 1 and "export held: " + PLACEHOLDERS in held.stderr, held.stdout + held.stderr
    assert not (project / "dist").exists()
    skill = project / "skills" / "demo-skill"
    write_the_skill(skill)
    again = b2s(project, *make_args("--target", "claude", "--target", "codex", "--out", "dist"))
    assert again.returncode == 0, again.stdout + again.stderr
    assert re.search(r"^build    skipped: SKILL.md already has an author \(--rebuild overwrites it\)$", again.stdout, re.M)
    assert "Chain with a semicolon in 5.1." in (skill / "SKILL.md").read_text(encoding="utf-8"), "an author's SKILL.md is never overwritten"
    assert re.search(r"^fill     nothing left to write$", again.stdout, re.M)
    for target in ("claude", "codex"):
        dest = project / "dist" / target / "demo-skill"
        assert (dest / "SKILL.md").is_file() and (dest / ".lock.json").is_file()
        lock = json.loads((dest / ".lock.json").read_text(encoding="utf-8"))
        assert lock["name"] == "demo-skill" and lock["target"] == target and lock["eval-rate"] == 1.0
        with zipfile.ZipFile(project / "dist" / target / "demo-skill.zip") as z:
            names = z.namelist()
        assert "SKILL.md" in names and not any(n.startswith(".") or "/." in n for n in names), names
        assert not any(p.is_dir() and p.name == "export" for p in dest.rglob("*")), "no export folder inside the copy"
    # the guard check of SKILL.md: nothing named export under skills, and no path near the limit
    assert not [p for p in (project / "skills").rglob("*") if p.is_dir() and p.name == "export"]
    assert max(len(str(p)) - len(str(project)) for p in project.rglob("*")) < 240
    # --rebuild gives the scaffold back
    rebuilt = b2s(project, *make_args("--rebuild"))
    assert rebuilt.returncode == 0 and "fill     " + PLACEHOLDERS in rebuilt.stdout


@live
def test_an_old_export_folder_inside_the_skill_never_ships(project: Path) -> None:
    b2s(project, *make_args())
    skill = project / "skills" / "demo-skill"
    write_the_skill(skill)
    (skill / "export" / "claude").mkdir(parents=True)
    (skill / "export" / "claude" / "stale.md").write_text("stale\n", encoding="utf-8")
    r = b2s(project, *make_args("--target", "claude", "--out", "dist"))
    assert r.returncode == 0, r.stdout + r.stderr
    assert not (project / "dist" / "claude" / "demo-skill" / "export").exists()
    with zipfile.ZipFile(project / "dist" / "claude" / "demo-skill.zip") as z:
        assert not any("stale" in n or "export" in n for n in z.namelist())


@live
def test_a_destination_path_over_240_characters_is_refused_before_anything_is_copied(project: Path) -> None:
    b2s(project, *make_args())
    write_the_skill(project / "skills" / "demo-skill")
    long_out = str(project / ("a" * 230))
    r = b2s(project, "export", "--skill", "skills/demo-skill", "--target", "claude", "--out", long_out, "--work", "work/demo-skill", "--qa", "qa.jsonl")
    assert r.returncode == 1 and "export refused:" in r.stderr and "limit 240" in r.stderr, r.stdout + r.stderr
    assert not (project / ("a" * 230)).exists()


@live
def test_the_eval_gate_refuses_and_nothing_is_exported(project: Path) -> None:
    (project / "qa.jsonl").write_text('{"q": "what about zzzznothere?", "must": ["zzzznothere"]}\n{"q": "what about qqqqmissing?", "must": ["qqqqmissing"]}\n', encoding="utf-8")
    r = b2s(project, *make_args("--target", "claude", "--out", "dist"))
    assert r.returncode == 1 and "eval gate refused: rate 0.000 below 0.6; fix the skill, not the test" in r.stderr, r.stdout + r.stderr
    assert not (project / "dist").exists()
    assert json.loads((project / "work" / "demo-skill" / "make.json").read_text(encoding="utf-8"))["gate"] == "refused"
    direct = b2s(project, "export", "--skill", "skills/demo-skill", "--target", "claude", "--out", "dist")
    assert direct.returncode == 1 and "eval gate refused export: rate 0.000 below 0.6" in direct.stderr
    assert not (project / "dist").exists()


@pytest.mark.parametrize("case,needle", [
    ("bad-name", "(rule: name matches dir, a-z0-9- only)"),
    ("name-not-the-folder", "must match skill dir"),
    ("no-qa", "not found"),
    ("wrong-qa-shape", 'must be {"q", "must"}'),
    ("missing-source", "--in nope.pdf not found"),
    ("work-in-skill", "inside each other"),
    ("work-in-source", "inside the source folder"),
    ("glob-matches-nothing", "matching 'nothing-*.md'"),
])
@live
def test_make_refusals_exit_two_and_build_no_skill(project: Path, case: str, needle: str) -> None:
    args = make_args()
    if case == "bad-name":
        args = make_args(name="Bad_Name")
    elif case == "name-not-the-folder":
        args += ["--skill", "skills/other-name"]
    elif case == "no-qa":
        (project / "qa.jsonl").unlink()
    elif case == "wrong-qa-shape":
        (project / "qa.jsonl").write_text('{"question": "x", "answer": "y"}\n', encoding="utf-8")
    elif case == "missing-source":
        args[args.index("--in") + 1] = "nope.pdf"
    elif case == "work-in-skill":
        args += ["--work", "skills/demo-skill/work"]
    elif case == "work-in-source":
        args += ["--work", "manual/work"]
    elif case == "glob-matches-nothing":
        args += ["--glob", "nothing-*.md"]
    r = b2s(project, *args)
    assert r.returncode == 2 and needle in r.stderr and "Traceback" not in r.stderr, r.stdout + r.stderr
    assert not (project / "skills").exists(), "no skill was built before the refusal"


@live
def test_a_question_ends_without_a_question_mark_because_punctuation_sticks_to_the_word(project: Path) -> None:
    for question, passes in (("xyzzy plugh objects?", False), ("xyzzy plugh objects", True)):  # only the last word is in the source
        (project / "qa.jsonl").write_text(json.dumps({"q": question, "must": ["objects"]}) + "\n", encoding="utf-8")
        r = b2s(project, *make_args("--work", f"work/w{int(passes)}", "--skill", "skills/demo-skill"))
        assert (r.returncode == 0) is passes, (question, r.stdout, r.stderr)
        assert ("eval     1/1 = 1.000" in r.stdout) is passes
        shutil.rmtree(project / "skills", ignore_errors=True)


@live
def test_glob_takes_only_the_matching_files_of_a_folder(project: Path) -> None:
    (project / "qa.jsonl").write_text('{"q": "what does a pipeline pass between commands?", "must": ["objects"]}\n', encoding="utf-8")
    r = b2s(project, *make_args("--glob", "pipe.*"))
    assert r.returncode == 0 and "extract  folder, " in r.stdout and ", 1 files" in r.stdout, r.stdout + r.stderr
    assert "semicolon" not in (project / "work" / "demo-skill" / "full_text.txt").read_text(encoding="utf-8")


@live
def test_a_docx_file_is_a_source(project: Path) -> None:
    docx = pytest.importorskip("docx")
    doc = docx.Document()
    doc.add_paragraph("Use a semicolon to chain commands. The operator exists only in PowerShell 7. A pipeline passes objects.")
    doc.save(str(project / "manual.docx"))
    args = make_args()
    args[args.index("--in") + 1] = "manual.docx"
    r = b2s(project, *args)
    assert r.returncode == 0 and r.stdout.startswith("extract  docx, "), r.stdout + r.stderr


def test_help_lists_every_stage() -> None:
    r = b2s(ROOT, "--help")
    assert r.returncode == 0
    for stage in ("make", "extract", "split", "index", "build", "audit", "eval", "refresh", "export"):
        assert re.search(rf"^  {stage}\s", r.stdout, re.M), stage


def test_the_budget_numbers_in_the_skill_match_the_gates() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8") + (SKILL / "references" / "stages.md").read_text(encoding="utf-8")
    assert f"{g.BODY_TOKEN_BUDGET} tokens" in text and f"{g.TOTAL_TOKEN_BUDGET} tokens" in text
    assert "0.6" in text and "240 characters" in text
    # the exit-code and message claims of SKILL.md are the ones the tests above ran
    for needle in ("export held", "eval gate refused", "fix the skill, not the test", "build skipped", "exit 2", "must be {\"q\", \"must\"}",
                   "Get-ChildItem skills -Recurse -Directory -Filter export", "tools/b2s.py make"):
        assert needle in text, needle


@live
def test_it_runs_through_pwsh_from_a_folder_with_spaces_and_writes_there(project: Path, tmp_path_factory) -> None:
    pwsh = shutil.which("pwsh")
    if pwsh is None:
        pytest.skip("pwsh 7 is not installed")
    spaced = tmp_path_factory.mktemp("my project") / "other repo"
    shutil.copytree(project, spaced)
    cmd = (f"& '{sys.executable}' '{B2S}' make --in manual --name demo-skill --description 'Use when chaining commands in PowerShell.' "
           f"--qa qa.jsonl; exit $LASTEXITCODE")
    r = subprocess.run([pwsh, "-NoLogo", "-NoProfile", "-NonInteractive", "-Command", cmd], cwd=spaced, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=180)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "eval     3/3 = 1.000 (gate 0.6)" in r.stdout
    assert (spaced / "skills" / "demo-skill" / "SKILL.md").is_file() and (spaced / "work" / "demo-skill" / "make.json").is_file()
    assert not (ROOT / "skills" / "demo-skill").exists()
