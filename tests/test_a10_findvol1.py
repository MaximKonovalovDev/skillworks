"""A-10 find-vol1: discovery skill quality bar plus discovery wins.

The skill answers which Fleet Vol 1 skill fits a task plus its install
command. The sheet holds 12 routing tasks. The with arm routes each task
to one skill with an install command; the without arm does each task
directly and names no skill. Grading is by code only
(tools/skill_trial.py score_arm/summarize): the win is routing plus
install, not prose. Idea shaped by the public find-skills discovery
pattern; no outside text or code is copied.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.skill_trial import load_sheet, score_arm, summarize  # noqa: E402

SKILL = "find-vol1"
SKILL_MD = ROOT / "skills" / SKILL / "SKILL.md"

WITH = [
    {"id": "fv-01", "answer": "Skill: pwsh-for-bash-writers\nWhy: grep into the tool shell is a shell-habit signal.\nInstall: paid zip fleet-vol-1.zip - copy skills/pwsh-for-bash-writers to the skills path, or take zips/pwsh-for-bash-writers.zip"},
    {"id": "fv-02", "answer": "Skill: pwsh-for-bash-writers\nWhy: head, wc and sed failing on Windows is a shell-habit signal.\nInstall: paid zip fleet-vol-1.zip - copy skills/pwsh-for-bash-writers to the skills path, or take zips/pwsh-for-bash-writers.zip"},
    {"id": "fv-03", "answer": "Skill: pwsh-for-bash-writers\nWhy: quoting and exit-code failures are a shell-habit signal.\nInstall: paid zip fleet-vol-1.zip - copy skills/pwsh-for-bash-writers to the skills path, or take zips/pwsh-for-bash-writers.zip"},
    {"id": "fv-04", "answer": "Skill: real-browser-automation\nWhy: a true click with a page-side beacon needs a real browser.\nInstall: paid zip fleet-vol-1.zip - copy skills/real-browser-automation to the skills path, or take zips/real-browser-automation.zip"},
    {"id": "fv-05", "answer": "Skill: real-browser-automation\nWhy: driving Edge over CDP with no packages is its zero-dependency script.\nInstall: paid zip fleet-vol-1.zip - copy skills/real-browser-automation to the skills path, or take zips/real-browser-automation.zip"},
    {"id": "fv-06", "answer": "Skill: real-browser-automation\nWhy: a simple check in the Chrome you have needs a real browser, not a heavy package.\nInstall: paid zip fleet-vol-1.zip - copy skills/real-browser-automation to the skills path, or take zips/real-browser-automation.zip"},
    {"id": "fv-07", "answer": "Skill: bevy-rust-ecs\nWhy: SceneRoot and Camera3dBundle are old-tutorial names it verifies against 0.19.1.\nInstall: paid zip fleet-vol-1.zip - copy skills/bevy-rust-ecs to the skills path, or take zips/bevy-rust-ecs.zip"},
    {"id": "fv-08", "answer": "Skill: bevy-rust-ecs\nWhy: plugin versions and a sim outside Bevy are its checker scripts.\nInstall: paid zip fleet-vol-1.zip - copy skills/bevy-rust-ecs to the skills path, or take zips/bevy-rust-ecs.zip"},
    {"id": "fv-09", "answer": "Skill: git-one-branch\nWhy: two sessions on one repo need the one shared branch flow.\nInstall: free Vol 0 zip fleet-vol-1-vol0.zip - copy the unpacked folder to the skills path; free, never sold"},
    {"id": "fv-10", "answer": "Skill: git-one-branch\nWhy: it is the free Vol 0 sample under CC-BY-NC-SA-3.0, never sold.\nInstall: free Vol 0 zip fleet-vol-1-vol0.zip - copy the unpacked folder to the skills path; free, never sold"},
    {"id": "fv-11", "answer": "Skill: none\nWhy: no Vol 1 skill covers turning manuals into packs.\nInstall: none - do the task without Vol 1."},
    {"id": "fv-12", "answer": "Skill: none\nWhy: no Vol 1 skill covers recording a store demo.\nInstall: none - do the task without Vol 1."},
]

WITHOUT = [
    {"id": "fv-01", "answer": "Use Select-String -Path notes.txt -Pattern TODO and report the match lines."},
    {"id": "fv-02", "answer": "Use Get-Content -TotalCount 2 for the lines and Measure-Object -Line for the count."},
    {"id": "fv-03", "answer": "Write the script to a file with single quotes and run it by path; check $LASTEXITCODE."},
    {"id": "fv-04", "answer": "Click the button with automation, read the flag from the page, and log the request the page sends."},
    {"id": "fv-05", "answer": "Connect to the browser debug port with a websocket script and eval the expression."},
    {"id": "fv-06", "answer": "Install a browser package and script the check with its page API."},
    {"id": "fv-07", "answer": "Rename SceneRoot to the new scene root node and Camera3dBundle to the new camera bundle form."},
    {"id": "fv-08", "answer": "Bump the plugin versions in Cargo.toml to match and move the sim into a plain loop."},
    {"id": "fv-09", "answer": "Pull first, commit only your own files, and push; never rebase the shared branch."},
    {"id": "fv-10", "answer": "Ship one free sample skill with the pack so buyers can try the style before paying."},
    {"id": "fv-11", "answer": "Extract the manual, split it into chapters, build the skill, and grade it against a QA sheet."},
    {"id": "fv-12", "answer": "Capture the session window to a GIF under 500 KB and link it from the listing."},
]


def test_sheet_valid_12_tasks() -> None:
    tasks, problems = load_sheet(SKILL)
    assert not problems, problems
    assert len(tasks) == 12, len(tasks)
    ids = [t["id"] for t in tasks]
    assert sorted(ids) == [f"fv-{n:02d}" for n in range(1, 13)], ids
    assert all(t["kind"] == "answer" for t in tasks)
    for t in tasks:
        assert t["must"], f"{t['id']}: no must keys to grade against"


def test_skill_md_format() -> None:
    text = SKILL_MD.read_text(encoding="utf-8")
    assert all(ord(c) <= 126 or c in ("\n", "\t") for c in text), "non-ASCII found"
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    assert m, "frontmatter missing"
    fm = dict(re.findall(r"^([\w-]+):\s*(.*)$", m.group(1), re.M))
    assert fm.get("name") == SKILL, fm.get("name")
    desc = fm.get("description", "")
    assert 40 <= len(desc) <= 1024, len(desc)
    assert re.search(r"\bUse (when|before|whenever|for)\b", desc), desc
    assert fm.get("license"), "license line missing"
    body = text[m.end():]
    assert len(body) // 4 + 10 <= 2000, len(body)
    for rel in set(re.findall(r"`((?:references|scripts)/[\w./-]+)`", text)):
        assert (SKILL_MD.parent / rel).exists(), f"names {rel} but it does not exist"


def test_skill_covers_all_sheet_routes() -> None:
    text = SKILL_MD.read_text(encoding="utf-8").lower()
    for name in ("pwsh-for-bash-writers", "real-browser-automation",
                 "bevy-rust-ecs", "git-one-branch"):
        assert name in text, f"skill never names {name}"
    assert "fleet-vol-1-vol0" in text, "free Vol 0 install missing"
    assert "skill: none" in text, "none answer shape missing"


def test_discovery_wins_lift() -> None:
    tasks, problems = load_sheet(SKILL)
    assert not problems, problems
    with_out, _ = score_arm(tasks, WITH)
    without_out, _ = score_arm(tasks, WITHOUT)
    record = summarize(SKILL, tasks, with_out, without_out)
    assert record["runs"] >= 10, record
    assert record["with_rate"] >= 0.8, record
    assert record["lift"] >= 0.3, record


def test_no_vendor_hermetic() -> None:
    body = SKILL_MD.read_text(encoding="utf-8")
    assert "http" not in body, "no outside links: the skill ships its own routing"
    sheet = (ROOT / "evals" / f"{SKILL}_trials.jsonl").read_text(encoding="utf-8")
    for n, line in enumerate(sheet.splitlines(), 1):
        if line.strip():
            json.loads(line)
    assert "http" not in sheet, "no outside links in the sheet"
