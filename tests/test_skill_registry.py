"""TS-7: skill_registry freeze plus lock-converge plus registry validate."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "skill_registry.py"


def run(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr)


def make_skills(base: Path) -> Path:
    skills = base / "skills"
    for name, fm in (("alpha", "name: alpha\ndescription: Pays bills.\nversion: 1.2.0\nlicense: MIT\n"),
                     ("beta", "name: beta\ndescription: Skips clean runs.\nversion: 0.3.1\nlicense: MIT\n")):
        d = skills / name
        (d / "scripts").mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\n{fm}---\n\n# {name}\nBody text here.\n", encoding="utf-8")
        (d / "scripts" / f"{name}.py").write_text(f"print({name!r})\n", encoding="utf-8")
    (skills / "alpha" / "eval_report.json").write_text(
        json.dumps({"skill": "alpha", "total": 4, "passed": 3, "rate": 0.75}), encoding="utf-8")
    return skills


def test_freeze_install_converge_and_registry_validates(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    manifest, lock = tmp_path / "manifest.json", tmp_path / "lock.json"
    code, out = run("freeze", "--skills", str(skills), "--manifest", str(manifest), "--lock", str(lock))
    assert code == 0, out
    assert "froze 2 skills" in out
    assert len(json.loads(lock.read_text(encoding="utf-8"))["skills"]["alpha"]["files"]) == 3

    dest = tmp_path / "installed"
    code, out = run("install", "--lock", str(lock), "--source", str(skills), "--to", str(dest))
    assert code == 0, out
    assert "RESULT CONVERGED" in out and "empty diff" in out

    code, out = run("install", "--lock", str(lock), "--source", str(skills), "--to", str(dest), "--check")
    assert code == 0, out
    assert "empty diff" in out

    (dest / "alpha" / "SKILL.md").write_text("tampered", encoding="utf-8")
    code, out = run("install", "--lock", str(lock), "--source", str(skills), "--to", str(dest), "--check")
    assert code == 1 and "changed SKILL.md" in out

    reg = tmp_path / "registry.json"
    code, out = run("registry", "--skills", str(skills), "--out", str(reg))
    assert code == 0, out
    entries = {e["name"]: e for e in json.loads(reg.read_text(encoding="utf-8"))["skills"]}
    assert entries["alpha"]["eval_rate"] == 0.75 and entries["alpha"]["above_gate"] is True
    assert entries["beta"]["eval_rate"] == 0.0 and entries["beta"]["above_gate"] is False
    assert all(e["source_pin"] for e in entries.values())

    code, out = run("validate", "--registry", str(reg), "--skills", str(skills))
    assert code == 0, out
    assert "RESULT PASS" in out


def test_help_exits_zero() -> None:
    assert run("--help")[0] == 0
