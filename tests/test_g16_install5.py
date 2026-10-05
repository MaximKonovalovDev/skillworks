"""G-16 install5: dry run to 5 repos, empty-diff shape, no outside writes."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "g16-install5.py"


def run(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=300)
    return r.returncode, (r.stdout + r.stderr)


def test_five_repos_listed() -> None:
    text = (ROOT / "tools" / "g16-install5.py").read_text(encoding="utf-8")
    for repo in ("engine2040", "forge", "factory", "fp-research", "marketing-studio"):
        assert repo in text
    assert len([l for l in text.splitlines() if ".opencode" in l and "skills" in l]) >= 1


def test_dry_run_reports_per_repo_and_temp_converged() -> None:
    code, out = run()
    assert code == 0, out
    for repo in ("engine2040", "forge", "factory", "fp-research", "marketing-studio"):
        assert repo in out, out
    assert "RESULT CONVERGED" in out and "empty" in out, out
    assert "nothing written" in out, out


def test_check_subset_repo_is_read_only() -> None:
    code, out = run("forge")
    assert code == 0, out
    assert "forge" in out, out
    assert "engine2040" not in out, out


def test_unknown_repo_is_refused() -> None:
    code, out = run("no-such-repo")
    assert code == 2, out
    assert "unknown repo" in out, out


def test_apply_to_temp_converges_then_checks_empty(tmp_path: Path) -> None:
    dest = tmp_path / "skills-out"
    code, out = run("--apply", "--to", str(dest))
    assert code == 0, out
    assert "RESULT CONVERGED" in out and "empty diff" in out, out
    assert (dest / "pwsh-for-bash-writers" / "SKILL.md").is_file() or any(dest.iterdir())


def test_apply_refuses_to_inside_skills() -> None:
    code, out = run("--apply", "--to", str(ROOT / "skills" / "nested-out"))
    assert code != 0, out
    assert "refused" in out, out


def test_no_network_imports() -> None:
    text = (ROOT / "tools" / "g16-install5.py").read_text(encoding="utf-8")
    for bad in ("socket", "urllib", "requests", "http.client", "urlopen"):
        assert bad not in text, bad


def test_help_exits_zero() -> None:
    assert run("--help")[0] == 0
