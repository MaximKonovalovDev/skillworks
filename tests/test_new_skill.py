"""tools/new_skill.py: stamp a fleet skill from skills/_template into a scratch root, check the slots, refuse bad input."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g
from book2skill import build as build_mod
from book2skill import eval as eval_mod

ROOT = g.ROOT
sys.path.insert(0, str(ROOT / "tools"))
import new_skill as ns  # noqa: E402

DESC = "Count the words of a text file. Use when a text file needs a word count before a model run."
NAME = "word-count"
SIX = ["skills/word-count/SKILL.md", "skills/word-count/references/sources.md", "skills/word-count/scripts/word_count.py",
       "tests/test_word_count.py", "evals/word-count_qa.jsonl", "evals/word-count_trials.jsonl"]


def cli(*args: str, root: Path | None = None) -> subprocess.CompletedProcess[str]:
    extra = ["--root", str(root)] if root else []
    return subprocess.run([sys.executable, str(ROOT / "tools" / "new_skill.py"), *args, *extra], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=60)


def tree(root: Path) -> list[str]:
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file())


def fill(root: Path, name: str = NAME) -> None:
    """Fill every slot with the same words and give the script a trivial work(): what a skill author does by hand."""
    script = ns.script_name(name)
    for path in ns.skill_files(name, root):
        text = ns.SLOT_RE.sub("filler words", path.read_text(encoding="utf-8"))
        if path.name == f"{script}.py":
            old = f'    print("ERROR not implemented: write work() in scripts/{script}.py")\n    return 2\n'
            assert old in text
            text = text.replace(old, '    print("DONE")\n    return 0\n')
        path.write_text(text, encoding="utf-8", newline="\n")


def test_the_stamp_writes_the_six_files_and_names_every_open_slot(tmp_path: Path) -> None:
    r = cli(NAME, DESC, root=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr
    assert tree(tmp_path) == sorted(SIX)
    assert r.stdout.splitlines()[0] == "STAMPED word-count: 6 files"
    open_lines = [ln for ln in r.stdout.splitlines() if ln.startswith("OPEN ")]
    assert len(open_lines) == sum(len(ns.open_slots(tmp_path / p)) for p in SIX) and len(open_lines) > 20
    assert "0 slots" not in r.stdout and "FLEET_SKILLS" in r.stdout and "tests/test_word_count.py" in r.stdout
    fm = g.frontmatter((tmp_path / SIX[0]).read_text(encoding="utf-8"))
    assert fm == {"name": NAME, "description": DESC, "license": "MIT"}
    for p in SIX:
        text = (tmp_path / p).read_text(encoding="utf-8")
        assert "{{name}}" not in text and "{{script}}" not in text and "{{description" not in text, p
        assert b"\r" not in (tmp_path / p).read_bytes(), p
    for p in SIX[:3]:  # the gates want plain ASCII in a skill folder
        assert all(ord(c) < 127 for c in (tmp_path / p).read_text(encoding="utf-8")), p
    assert g.test_file_for(NAME).name == Path(SIX[3]).name, "the test file is where skill_gates looks for it"


def test_the_stamped_script_has_help_and_exits_nonzero_until_it_is_written(tmp_path: Path) -> None:
    ns.stamp(NAME, DESC, tmp_path)
    script = tmp_path / SIX[2]
    h = subprocess.run([sys.executable, str(script), "--help"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert h.returncode == 0 and "--input" in h.stdout and "--out" in h.stdout and DESC[:30] in h.stdout
    r = subprocess.run([sys.executable, str(script), "--input", "a", "--out", "b"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert r.returncode == 2 and r.stdout.startswith("ERROR not implemented"), r.stdout + r.stderr


def test_check_exits_one_while_a_slot_is_left_and_zero_when_none_is(tmp_path: Path) -> None:
    ns.stamp(NAME, DESC, tmp_path)
    r = cli("--check", NAME, root=tmp_path)
    assert r.returncode == 1 and r.stdout.splitlines()[-1].startswith("RESULT OPEN: word-count has ") and "OPEN skills/word-count/SKILL.md:9:" in r.stdout
    assert "not implemented" in r.stdout
    fill(tmp_path)
    r = cli("--check", NAME, root=tmp_path)
    assert r.returncode == 0 and r.stdout.strip() == "RESULT DONE: word-count has no slot left in 6 files", r.stdout
    one = tmp_path / SIX[1]  # one slot back in a reference file is found too
    one.write_text(one.read_text(encoding="utf-8") + "\n{{slot: say where the idea comes from}}\n", encoding="utf-8")
    r = cli("--check", NAME, root=tmp_path)
    assert r.returncode == 1 and "sources.md:" in r.stdout and "say where the idea comes from" in r.stdout


def test_the_stamped_tests_pass_once_the_script_has_a_trivial_work(tmp_path: Path) -> None:
    ns.stamp(NAME, DESC, tmp_path)
    fill(tmp_path)
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tests"), SKILL_LIVE="1")  # the stock helper and the gates come from this repo
    ini = tmp_path / "pytest.ini"  # without its own root pytest would scan the whole temp folder, a big and busy tree
    ini.write_text("[pytest]\n", encoding="utf-8")
    r = subprocess.run([sys.executable, "-m", "pytest", str(tmp_path / SIX[3]), "-q", "-p", "no:cacheprovider", "-c", str(ini), "--rootdir", str(tmp_path)],
                       cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=300)
    last = r.stdout.strip().splitlines()[-1]
    assert r.returncode == 0 and "failed" not in last and "error" not in last, r.stdout + r.stderr
    assert re.search(r"\b3 passed\b", last) or (re.search(r"\b2 passed\b", last) and "1 skipped" in last), last  # skipped only when pwsh 7 is missing
    script = tmp_path / SIX[2]
    done = subprocess.run([sys.executable, str(script), "--input", "a", "--out", "b"], capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    assert done.returncode == 0 and done.stdout.strip() == "DONE"


def test_the_stamped_qa_file_has_the_gate_shape_and_the_filled_skill_clears_the_eval_gate(tmp_path: Path) -> None:
    ns.stamp(NAME, DESC, tmp_path)
    qa = tmp_path / SIX[4]
    eval_mod.validate_qa(qa)  # {"q", "must"} on every row, slots included
    rows = [json.loads(ln) for ln in qa.read_text(encoding="utf-8").splitlines()]
    assert len(rows) >= g.QA_MIN and all(isinstance(r["q"], str) and isinstance(r["must"], list) and r["must"] for r in rows)
    trials = [json.loads(ln) for ln in (tmp_path / SIX[5]).read_text(encoding="utf-8").splitlines()]
    assert {t["kind"] for t in trials} == {"run", "answer"} and len({t["id"] for t in trials}) == len(trials)
    assert any(t.get("must_not") for t in trials), "the must_not rows live in the trial sheet, which is where tools/skill_trial.py reads them"
    fill(tmp_path)
    scratch = tmp_path / "grade"
    (scratch / "skill").mkdir(parents=True)
    for md in (tmp_path / "skills" / NAME).rglob("*.md"):
        (scratch / "skill" / md.name).write_text(md.read_text(encoding="utf-8"), encoding="utf-8")
    report = eval_mod.run_eval(scratch / "work", scratch / "skill", qa)
    assert report["rate"] >= g.EVAL_GATE, report


@pytest.mark.parametrize("name", ["Bad_Name", "trail-", "a--b", "has space", "_template", "x" * 65, "", "café"])
def test_a_bad_name_is_refused_and_nothing_is_written(tmp_path: Path, name: str) -> None:
    r = cli(name, DESC, root=tmp_path)
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused: bad name"), r.stdout + r.stderr
    assert tree(tmp_path) == []


@pytest.mark.parametrize("desc,needle", [
    ("Too short. Use when x.", "characters, want 40-1024"),
    ("Counts the words of a text file for a batch run, with no trigger sentence at all.", "needs a trigger"),
    ("Count the words of a text file.\nUse when a text file needs a word count.", "one line"),
    ("Count the wörds of a text file. Use when a text file needs a word count.", "non-ASCII"),
])
def test_a_bad_description_is_refused_and_nothing_is_written(tmp_path: Path, desc: str, needle: str) -> None:
    r = cli(NAME, desc, root=tmp_path)
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused:") and needle in r.stdout, r.stdout + r.stderr
    assert tree(tmp_path) == []


@pytest.mark.parametrize("existing", SIX)
def test_an_existing_file_of_the_skill_refuses_the_stamp_and_is_left_as_it_was(tmp_path: Path, existing: str) -> None:
    f = tmp_path / existing
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_bytes(b"mine\n")
    r = cli(NAME, DESC, root=tmp_path)
    assert r.returncode == 2 and r.stdout.startswith("ERROR refused: word-count already has") and existing in r.stdout, r.stdout
    assert tree(tmp_path) == [existing] and f.read_bytes() == b"mine\n"


def test_a_skill_is_never_stamped_twice(tmp_path: Path) -> None:
    assert cli(NAME, DESC, root=tmp_path).returncode == 0
    before = {p: (tmp_path / p).read_bytes() for p in SIX}
    r = cli(NAME, DESC.replace("Count", "Tally"), root=tmp_path)
    assert r.returncode == 2 and "already has" in r.stdout
    assert {p: (tmp_path / p).read_bytes() for p in SIX} == before


def test_usage_errors_exit_two(tmp_path: Path) -> None:
    assert cli(NAME, root=tmp_path).returncode == 2                        # no description
    assert cli("--check", NAME, DESC, root=tmp_path).returncode == 2       # --check takes only the name
    r = cli("--check", NAME, root=tmp_path)                                # nothing stamped yet
    assert r.returncode == 2 and r.stdout.startswith("ERROR no skill word-count")
    r = cli(NAME, DESC, root=tmp_path / "nowhere")
    assert r.returncode == 2 and "is not a folder" in r.stdout
    assert cli("--check", "Bad_Name", root=tmp_path).returncode == 2


def test_the_name_rule_is_the_one_the_build_stage_uses() -> None:
    assert ns.NAME_RE.pattern == build_mod.NAME_RE.pattern


def test_the_template_folder_still_serves_the_book_scaffold_test_and_the_real_donor_has_no_slot_left() -> None:
    text = (ROOT / "skills" / "_template" / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---") and "name:" in text and "description:" in text  # what tests/test_pipeline.py reads
    for template, _ in ns.targets(NAME, ROOT):
        assert (ROOT / "skills" / "_template" / template).is_file(), template
    r = cli("--check", "pipe-run")  # the skill the template was shaped from
    assert r.returncode == 0 and r.stdout.startswith("RESULT DONE: pipe-run has no slot left"), r.stdout
