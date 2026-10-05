"""G-18: g18-lock writes a lockfile and converge proves the three agree."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "g18-lock.py"


def run(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT,
                       capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr)


def make_skills(base: Path) -> Path:
    skills = base / "skills"
    for name, ver in (("alpha", "1.2.0"), ("beta", "0.3.1")):
        d = skills / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Demo skill.\nversion: {ver}\n---\n\n# {name}\nBody.\n",
            encoding="utf-8")
        (d / "run.py").write_text(f"print({name!r})\n", encoding="utf-8")
    (skills / "alpha" / "eval_report.json").write_text(
        json.dumps({"skill": "alpha", "total": 4, "passed": 3, "rate": 0.75}), encoding="utf-8")
    return skills


def write_manifest_and_registry(skills: Path, base: Path) -> tuple[Path, Path]:
    manifest = base / "manifest.json"
    manifest.write_text(json.dumps({"generated_at": "t", "source_pin": "abc1234",
                                    "skills": [{"name": "alpha", "version": "1.2.0"},
                                               {"name": "beta", "version": "0.3.1"}]}), encoding="utf-8")
    registry = base / "registry.json"
    registry.write_text(json.dumps({"generated_at": "t", "source_pin": "abc1234",
                                    "skills": [{"name": "alpha", "version": "1.2.0", "eval_rate": 0.75},
                                               {"name": "beta", "version": "0.3.1", "eval_rate": 0.0}]}),
                        encoding="utf-8")
    return manifest, registry


def test_lock_writes_pinned_versions_and_hashes(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    lock = tmp_path / "lock.json"
    code, out = run("lock", "--skills", str(skills), "--out", str(lock))
    assert code == 0, out
    assert "locked 2 skills" in out
    data = json.loads(lock.read_text(encoding="utf-8"))
    assert data["skills"]["alpha"]["version"] == "1.2.0"
    assert len(data["skills"]["alpha"]["files"]["SKILL.md"]) == 64
    assert data["skills"]["beta"]["version"] == "0.3.1"


def test_converge_proves_manifest_lock_registry(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    manifest, registry = write_manifest_and_registry(skills, tmp_path)
    lock = tmp_path / "lock.json"
    assert run("lock", "--skills", str(skills), "--out", str(lock))[0] == 0
    code, out = run("converge", "--manifest", str(manifest), "--lock", str(lock),
                    "--registry", str(registry), "--skills", str(skills))
    assert code == 0, out
    assert "RESULT CONVERGED: 2 skills" in out


def test_range_versions_rejected(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    (skills / "beta" / "SKILL.md").write_text(
        "---\nname: beta\ndescription: Demo.\nversion: ^0.3.0\n---\n\n# beta\nBody.\n", encoding="utf-8")
    lock = tmp_path / "lock.json"
    code, out = run("lock", "--skills", str(skills), "--out", str(lock))
    assert code == 2 and "range version rejected" in out
    (skills / "beta" / "SKILL.md").write_text(
        "---\nname: beta\ndescription: Demo.\nversion: 0.3\n---\n\n# beta\nBody.\n", encoding="utf-8")
    code, out = run("lock", "--skills", str(skills), "--out", str(lock))
    assert code == 2 and "range version rejected" in out


def test_converge_catches_drift_and_tamper(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    manifest, registry = write_manifest_and_registry(skills, tmp_path)
    lock = tmp_path / "lock.json"
    assert run("lock", "--skills", str(skills), "--out", str(lock))[0] == 0
    reg = json.loads(registry.read_text(encoding="utf-8"))
    reg["skills"][0]["version"] = "1.3.0"
    registry.write_text(json.dumps(reg), encoding="utf-8")
    code, out = run("converge", "--manifest", str(manifest), "--lock", str(lock),
                    "--registry", str(registry), "--skills", str(skills))
    assert code == 1 and "version drift" in out
    reg["skills"][0]["version"] = "1.2.0"
    registry.write_text(json.dumps(reg), encoding="utf-8")
    (skills / "alpha" / "run.py").write_text("print('tampered')\n", encoding="utf-8")
    code, out = run("converge", "--manifest", str(manifest), "--lock", str(lock),
                    "--registry", str(registry), "--skills", str(skills))
    assert code == 1 and "changed file run.py" in out


def test_help_exits_zero() -> None:
    assert run("--help")[0] == 0
