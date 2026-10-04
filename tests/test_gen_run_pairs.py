"""tools/gen_run_pairs.py: the four scripts/run_pairs.py copies are made from one source, and a drifted copy fails."""
import ast
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import skill_gates as g

ROOT = g.ROOT
sys.path.insert(0, str(ROOT / "tools"))
import gen_run_pairs as gen  # noqa: E402

SKILLS = sorted(gen.VARIANTS)


def cli(*args: str, root: Path | None = None) -> subprocess.CompletedProcess[str]:
    extra = ["--root", str(root)] if root else []
    return subprocess.run([sys.executable, str(ROOT / "tools" / "gen_run_pairs.py"), *args, *extra], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL, timeout=60)


def scratch_root(tmp_path: Path) -> Path:
    for skill in SKILLS:
        dest = gen.target(tmp_path, skill)
        dest.parent.mkdir(parents=True)
        shutil.copyfile(gen.target(ROOT, skill), dest)
    return tmp_path


def test_the_four_copies_are_byte_for_byte_what_the_one_source_makes() -> None:
    assert SKILLS == ["edit-reread", "engine-builder", "pwsh-for-bash-writers", "repo-read-first"]
    on_disk = sorted(p.parent.parent.name for p in (ROOT / "skills").glob("*/scripts/run_pairs.py"))
    assert on_disk == SKILLS, "a skill with a run_pairs.py that the generator does not know"
    for skill in SKILLS:
        have = gen.target(ROOT, skill).read_bytes().replace(b"\r\n", b"\n")
        assert have == gen.render(skill).encode("utf-8"), f"skills/{skill}/scripts/run_pairs.py drifted: edit tools/run_pairs.tmpl, then python tools/gen_run_pairs.py"
    assert gen.drifted(ROOT) == []
    assert cli("--check").returncode == 0


def test_the_shared_code_is_in_the_source_once_and_only_the_variant_lines_differ() -> None:
    template = gen.TEMPLATE.read_text(encoding="utf-8")
    assert template.count("DRIVER = r") == 1 and template.count("def run_pairs(") == 1 and template.count("def main(") == 1
    texts = {s: gen.render(s).splitlines() for s in SKILLS}
    base = set(texts["engine-builder"])
    for twin in ("edit-reread", "repo-read-first"):
        assert len(set(texts[twin]) - base) <= 5, "the three eb copies differ only in 2 prose lines, 2 usage lines and the temp-folder tag"
    assert len(set(texts["pwsh-for-bash-writers"]) - base) <= 21  # the PATH strip, the tool check, the skip rule and their docstring
    assert len(template.splitlines()) < sum(len(t) for t in texts.values()) / 3, "the source is one copy plus markers, not four"


def test_a_drifted_copy_fails_the_check_and_the_generator_puts_it_back(tmp_path: Path) -> None:
    root = scratch_root(tmp_path)
    assert cli("--check", root=root).returncode == 0
    victim = gen.target(root, "edit-reread")
    victim.write_text(victim.read_text(encoding="utf-8").replace("--json", "--JSON", 1), encoding="utf-8", newline="\n")
    r = cli("--check", root=root)
    assert r.returncode == 1 and "DRIFT edit-reread" in r.stdout and r.stdout.count("ok   ") == 3, r.stdout
    fixed = cli(root=root)
    assert fixed.returncode == 0 and "updated edit-reread" in fixed.stdout and fixed.stdout.count("current ") == 3, fixed.stdout
    assert cli("--check", root=root).returncode == 0
    assert victim.read_bytes() == gen.render("edit-reread").encode("utf-8")


def test_a_missing_copy_counts_as_drift_and_is_written(tmp_path: Path) -> None:
    root = scratch_root(tmp_path)
    gen.target(root, "repo-read-first").unlink()
    assert gen.drifted(root) == ["repo-read-first"] and cli("--check", root=root).returncode == 1
    assert cli(root=root).returncode == 0 and gen.target(root, "repo-read-first").is_file()


def test_a_crlf_checkout_is_not_drift(tmp_path: Path) -> None:
    root = scratch_root(tmp_path)
    path = gen.target(root, "engine-builder")
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert gen.drifted(root) == []


@pytest.mark.parametrize("skill", SKILLS)
def test_each_copy_imports_only_the_standard_library_so_a_skill_folder_copied_alone_works(skill: str) -> None:
    tree = ast.parse(gen.target(ROOT, skill).read_text(encoding="utf-8"))
    imported = {a.name.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
    imported |= {n.module.split(".")[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= set(sys.stdlib_module_names), imported - set(sys.stdlib_module_names)


@pytest.mark.parametrize("skill", ["engine-builder", "pwsh-for-bash-writers"])
def test_a_generated_copy_runs_alone_in_a_folder_with_no_repo_around_it(tmp_path: Path, skill: str) -> None:
    if shutil.which("pwsh") is None:
        pytest.skip("pwsh 7 is not installed")
    lone = tmp_path / "other repo" / "skills" / skill
    (lone / "scripts").mkdir(parents=True)
    (lone / "references").mkdir()
    (lone / "scripts" / "run_pairs.py").write_text(gen.render(skill), encoding="utf-8", newline="\n")
    doc = {"fixture": {"a.txt": "hello\n"}, "pairs": [{"id": "p1", "bad": "Get-Content nothing.txt -ErrorAction Stop", "bad_error": "Cannot find path",
                                                        "good": "Get-Content a.txt", "expect": "hello"}]}
    (lone / "references" / "pairs.json").write_text(json.dumps(doc), encoding="utf-8")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    r = subprocess.run([sys.executable, str(lone / "scripts" / "run_pairs.py")], cwd=elsewhere, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", stdin=subprocess.DEVNULL, timeout=180, env={k: v for k, v in os.environ.items() if k != "PYTHONPATH"})
    assert r.returncode == 0 and r.stdout.splitlines() == ["PASS p1 ", "1 of 1 pairs behave as written"], r.stdout + r.stderr
    assert not list(elsewhere.iterdir())
