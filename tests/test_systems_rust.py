"""systems-rust: ownership, borrows, scoped threads, and C boundaries from Blandy.

Offline tests (default run): every SKILL.md rule line carries a chunk locator
that resolves to work/b1-progrust/chunks, every QA and trial must-word is
literally present in the skill text, no scaffold text remains, the sheet holds
12 tasks, the trial proof meets its gates, the eval report meets the export
gate, and the five rustc snippets behave as written (two refused with E0382
and E0499, three compile and run with exact stdout).
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import skill_gates as g
from book2skill import build as build_mod
from book2skill import distill as distill_mod
from tools import skill_trial as trial

NAME = "systems-rust"
SKILL = g.SKILLS / NAME
WORK = g.ROOT / "work" / "b1-progrust"
CHUNKS = WORK / "chunks"

pytestmark = pytest.mark.skipif(not (SKILL / "SKILL.md").is_file(), reason="skill not built yet")
needs_rustc = pytest.mark.skipif(shutil.which("rustc") is None, reason="rustc is not installed")

RULE_RE = re.compile(r"^\s*[-*]\s+.*`[^`]+`.*$")
CHUNK_RE = re.compile(r"`((?:chunks/)?(\d{4})\.txt)`")


def _body() -> str:
    return g.body_of((SKILL / "SKILL.md").read_text(encoding="utf-8"))


def _rules() -> list:
    return [ln for ln in _body().splitlines() if RULE_RE.match(ln)]


def test_every_rule_line_carries_a_chunk_locator() -> None:
    rules = _rules()
    assert len(rules) >= 20, f"only {len(rules)} rule lines"
    for ln in rules:
        assert ln.rstrip().endswith("]") and "[src:" in ln, f"rule without a trailing [src: ...]: {ln[:80]}"
        found = CHUNK_RE.findall(ln)
        assert found, f"rule without a chunk locator: {ln[:80]}"
        for _full, _num in found:
            base = _full.split("/")[-1]
            assert (CHUNKS / base).is_file(), f"locator {base} resolves to no chunk"


def test_no_scaffold_text_remains() -> None:
    assert build_mod.scaffold_leftovers(SKILL) == []
    assert build_mod._scaffold_body(NAME) not in _body()
    assert distill_mod.SCAFFOLD_SENTENCE not in _body()


def test_qa_musts_literally_appear_in_the_skill_text() -> None:
    text = g.skill_text(NAME).lower()
    rows = 0
    for line in (g.ROOT / "evals" / f"{NAME}_qa.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows += 1
        row = json.loads(line)
        assert set(row) == {"q", "must"}, row
        for m in row["must"]:
            assert m.lower() in text, f"must {m!r} is not in the skill text (question: {row['q']})"
    assert rows == 12, f"want 12 QA rows, have {rows}"


def test_trial_musts_literally_appear_in_the_skill_text() -> None:
    text = g.skill_text(NAME).lower()
    tasks, problems = trial.load_sheet(NAME)
    assert not problems, problems
    assert len(tasks) == 12, f"want 12 trial tasks, have {len(tasks)}"
    for task in tasks:
        for m in task.get("must", []):
            assert m.lower() in text, f"must {m!r} is not in the skill text (task: {task['id']})"


def test_skill_body_within_budget() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert g.body_tokens(text) <= g.BODY_TOKEN_BUDGET


def test_no_private_paths_in_the_public_skill() -> None:
    for p in SKILL.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".json"}:
            t = p.read_text(encoding="utf-8")
            assert not re.search(r"[A-Za-z]:\\Users\\|/Users/[a-z]|ghp_|github_pat_", t), f"{p.name} has a private path or token-like text"


def test_sources_manifest_lists_all_chunks() -> None:
    manifest = (SKILL / "references" / "sources.md").read_text(encoding="utf-8")
    chunks = sorted(p.name for p in CHUNKS.glob("*.txt"))
    assert chunks, "work/b1-progrust/chunks is empty; run split first"
    for name in chunks:
        assert f"`{name}`" in manifest, f"{name} missing from sources.md"


def test_trial_proof_meets_gates() -> None:
    proof = json.loads((SKILL / "references" / "trial-proof.json").read_text(encoding="utf-8"))
    assert proof["runs"] >= 10, proof
    assert proof["with_rate"] >= 0.8, proof
    assert proof["lift"] >= 0.3, proof
    assert proof["ok"] is True, proof


def test_eval_report_meets_export_gate() -> None:
    report = json.loads((SKILL / "eval_report.json").read_text(encoding="utf-8"))
    assert report["total"] == 12, report
    assert report["rate"] >= 0.6, report
    assert report["graded_on"] == "skill", report


SNIPS = {
    "move_err.rs": (
        "fn main() {\n"
        "    let s1 = String::from(\"hello\");\n"
        "    let s2 = s1;\n"
        "    println!(\"{s1} {s2}\");\n"
        "}\n"
    ),
    "borrow_err.rs": (
        "fn main() {\n"
        "    let mut y = 1;\n"
        "    let m1 = &mut y;\n"
        "    let m2 = &mut y;\n"
        "    println!(\"{m1} {m2}\");\n"
        "}\n"
    ),
    "box_own.rs": (
        "fn main() {\n"
        "    let point = Box::new((0.625, 0.5));\n"
        "    println!(\"{point:?}\");\n"
        "}\n"
    ),
    "rc_share.rs": (
        "use std::rc::Rc;\n"
        "fn main() {\n"
        "    let s: Rc<String> = Rc::new(\"shirataki\".to_string());\n"
        "    let t = s.clone();\n"
        "    let u = s.clone();\n"
        "    println!(\"{} {} {}\", Rc::strong_count(&s), t, u);\n"
        "}\n"
    ),
    "scoped_bands.rs": (
        "fn render(band: &mut [u8], val: u8) {\n"
        "    for b in band.iter_mut() {\n"
        "        *b = val;\n"
        "    }\n"
        "}\n"
        "fn main() {\n"
        "    let mut pixels = vec![0u8; 12];\n"
        "    let bands = pixels.chunks_mut(4);\n"
        "    std::thread::scope(|spawner| {\n"
        "        for (i, band) in bands.enumerate() {\n"
        "            spawner.spawn(move || render(band, (i + 1) as u8));\n"
        "        }\n"
        "    });\n"
        "    println!(\"{pixels:?}\");\n"
        "}\n"
    ),
}


def _compile(tmp_path: Path, name: str) -> subprocess.CompletedProcess:
    rs = tmp_path / name
    rs.write_text(SNIPS[name], encoding="utf-8")
    exe = tmp_path / (rs.stem + ".exe")
    return subprocess.run(["rustc", "--edition", "2021", str(rs), "-o", str(exe)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=180)


@needs_rustc
def test_use_after_move_is_refused_with_E0382(tmp_path: Path) -> None:
    r = _compile(tmp_path, "move_err.rs")
    assert r.returncode == 1, r.stderr
    assert "E0382" in r.stderr and "borrow of moved value" in r.stderr


@needs_rustc
def test_double_mutable_borrow_is_refused_with_E0499(tmp_path: Path) -> None:
    r = _compile(tmp_path, "borrow_err.rs")
    assert r.returncode == 1, r.stderr
    assert "E0499" in r.stderr and "more than once" in r.stderr


@needs_rustc
@pytest.mark.parametrize("name, want", [
    ("box_own.rs", "(0.625, 0.5)"),
    ("rc_share.rs", "3 shirataki shirataki"),
    ("scoped_bands.rs", "[1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3]"),
])
def test_good_programs_compile_and_print(tmp_path: Path, name: str, want: str) -> None:
    c = _compile(tmp_path, name)
    assert c.returncode == 0, c.stderr
    exe = tmp_path / (Path(name).stem + ".exe")
    r = subprocess.run([str(exe)], capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=60)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == want, r.stdout
