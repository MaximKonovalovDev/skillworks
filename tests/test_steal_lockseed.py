"""Steal lockseed: committed-lock seeding keeps compatible pins, reports true drift."""
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TOOL = ROOT / "tools" / "g18-lock.py"
def run(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(TOOL), *args], cwd=ROOT, capture_output=True, text=True, timeout=120)
    return r.returncode, (r.stdout + r.stderr)
def make_skills(base: Path) -> Path:
    skills = base / "skills"
    for name, ver in (("alpha", "1.2.0"), ("beta", "0.3.1")):
        d = skills / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Demo skill.\nversion: {ver}\n---\n\n# {name}\nBody.\n", encoding="utf-8")
        (d / "run.py").write_text(f"print({name!r})\n", encoding="utf-8")
    return skills
def write_manifest_and_registry(base: Path) -> tuple[Path, Path]:
    manifest = base / "manifest.json"
    manifest.write_text(json.dumps({"generated_at": "t", "source_pin": "abc1234", "skills": [{"name": "alpha", "version": "1.2.0"}, {"name": "beta", "version": "0.3.1"}]}), encoding="utf-8")
    registry = base / "registry.json"
    registry.write_text(json.dumps({"generated_at": "t", "source_pin": "abc1234", "skills": [{"name": "alpha", "version": "1.2.0", "eval_rate": 0.75}, {"name": "beta", "version": "0.3.1", "eval_rate": 0.0}]}), encoding="utf-8")
    return manifest, registry
def test_compatible_recheck_converged(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    manifest, registry = write_manifest_and_registry(tmp_path)
    lock = tmp_path / "lock.json"
    assert run("lock", "--skills", str(skills), "--out", str(lock))[0] == 0
    code, out = run("converge", "--manifest", str(manifest), "--lock", str(lock), "--registry", str(registry), "--skills", str(skills))
    assert code == 0, out
    assert "RESULT CONVERGED" in out
    assert out.count("STALE") == 0
def test_compatible_stable_metadata_only(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    manifest, registry = write_manifest_and_registry(tmp_path)
    lock = tmp_path / "lock.json"
    assert run("lock", "--skills", str(skills), "--out", str(lock))[0] == 0
    data = json.loads(lock.read_text(encoding="utf-8"))
    data["generated_at"] = "2099-01-01T00:00Z"
    data["source_pin"] = "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
    lock.write_text(json.dumps(data, indent=2), encoding="utf-8")
    code, out = run("converge", "--manifest", str(manifest), "--lock", str(lock), "--registry", str(registry), "--skills", str(skills))
    assert code == 0, out
    assert "RESULT CONVERGED" in out
    assert "STALE" not in out
def test_real_drift_still_stale(tmp_path: Path) -> None:
    skills = make_skills(tmp_path)
    manifest, registry = write_manifest_and_registry(tmp_path)
    lock = tmp_path / "lock.json"
    assert run("lock", "--skills", str(skills), "--out", str(lock))[0] == 0
    reg = json.loads(registry.read_text(encoding="utf-8"))
    reg["skills"][0]["version"] = "9.9.9"
    registry.write_text(json.dumps(reg), encoding="utf-8")
    code, out = run("converge", "--manifest", str(manifest), "--lock", str(lock), "--registry", str(registry), "--skills", str(skills))
    assert code == 1 and "STALE" in out and "version drift" in out
    reg["skills"][0]["version"] = "1.2.0"
    registry.write_text(json.dumps(reg), encoding="utf-8")
    (skills / "alpha" / "run.py").write_text("print('tampered')\n", encoding="utf-8")
    code2, out2 = run("converge", "--manifest", str(manifest), "--lock", str(lock), "--registry", str(registry), "--skills", str(skills))
    assert code2 == 1 and "STALE" in out2
